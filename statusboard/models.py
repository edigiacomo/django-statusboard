from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver

from model_utils.models import TimeStampedModel

from .settings import statusconf


SERVICE_STATUSES = (
    (0, _('Operational')),
    (1, _('Performance issues')),
    (2, _('Partial outage')),
    (3, _('Major outage')),
)


class ServiceQuerySet(models.QuerySet):
    def worst_status(self):
        """Return worst status in queryset."""
        return self.aggregate(models.Max('status'))['status__max']

    def worst_service(self):
        return self.latest('status')

    def uncategorized(self):
        return self.annotate(group_count=models.Count('groups')).filter(group_count=0)

    def priority_sorted(self):
        return self.order_by('-priority', 'name')


class ServiceManager(models.Manager):
    def get_queryset(self):
        return ServiceQuerySet(self.model, using=self._db)

    def worst_status(self):
        """Return worst status in queryset."""
        return self.get_queryset().worst_status()

    def uncategorized(self):
        return self.get_queryset().uncategorized()

    def priority_sorted(self):
        return self.get_queryset().priority_sorted()


class Service(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("name"))
    description = models.TextField(verbose_name=_("description"), blank=True)
    href = models.URLField(blank=True)
    status = models.IntegerField(choices=SERVICE_STATUSES, verbose_name=_("status"))
    priority = models.PositiveIntegerField(default=0, verbose_name=_("priority"))
    groups = models.ManyToManyField('ServiceGroup',
                                    related_name='services',
                                    related_query_name='service',
                                    verbose_name=_("groups"))
    objects = ServiceManager()

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        self._status = self.status

    def save(self, *args, **kwargs):
        # When the instance is saved, the original status is updated
        super(Service, self).save(*args, **kwargs)
        self._status = self.status

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")


SERVICEGROUP_COLLAPSE_OPTIONS = (
    (0, _('Never collapse')),
    (1, _('Always collapse')),
    (2, _('Collapse when all the services are operational')),
)


class ServiceGroupQuerySet(models.QuerySet):
    def priority_sorted(self):
        return self.order_by('-priority', 'name')


class ServiceGroupManager(models.Manager):
    def get_queryset(self):
        return ServiceGroupQuerySet(self.model, using=self._db)

    def priority_sorted(self):
        return self.get_queryset().priority_sorted()


class ServiceGroup(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("name"))
    priority = models.PositiveIntegerField(default=0, verbose_name=_("priority"))
    collapse = models.IntegerField(choices=SERVICEGROUP_COLLAPSE_OPTIONS,
                                   default=0)
    objects = ServiceGroupManager()

    def worst_service(self):
        return self.services.all().latest('status')

    def collapsed(self):
        """Check if the service group should collapse or not.

        Return true if a group doesn't have any service."""
        if self.collapse == 0:
            return False
        elif self.collapse == 1:
            return True
        else:
            return not self.services.exclude(status=0).exists()

    def is_empty_group(self):
        return not self.services.all().exists()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("service group")
        verbose_name_plural = _("service groups")


INCIDENT_STATUSES = (
    (0, _("Investigating")),
    (1, _("Identified")),
    (2, _("Watching")),
    (3, _("Fixed")),
)


class IncidentQuerySet(models.QuerySet):
    def occurred_in_last_n_days_q(self, days):
        """Q obects for the incidents occurred in last N days (1 = today)."""
        threshold = timezone.now() - timezone.timedelta(days=days-1)
        threshold = threshold.replace(hour=0, minute=0, second=0, microsecond=0)
        return models.Q(occurred__gte=threshold)

    def last_occurred_q(self):
        return self.occurred_in_last_n_days_q(statusconf.INCIDENT_DAYS_IN_INDEX)

    def occurred_in_last_n_days(self, days=7):
        """Return incidents occurred in last N days (1 = today)."""
        return self.filter(self.occurred_in_last_n_days_q(days))

    def last_occurred(self):
        """Return incidents occurred in last days. The number of days is defined
        in STATUSBOARD["INCIDENT_DAYS_IN_INDEX"]."""
        return self.filter(self.last_occurred_q())

    def in_index(self):
        q = self.last_occurred_q()
        if statusconf.OPEN_INCIDENT_IN_INDEX:
            q = q | models.Q(closed=False)

        return self.filter(q)


class IncidentManager(models.Manager):
    def get_queryset(self):
        return IncidentQuerySet(self.model, using=self._db)

    def occurred_in_last_n_days(self, days=7):
        """Return incidents occurred in last N days (1 = today)."""
        return self.get_queryset().occurred_in_last_n_days(days=days)

    def last_occurred(self):
        """Return incidents occurred in last days. The number of days is defined
        in STATUSBOARD["INCIDENT_DAYS_IN_INDEX"]."""
        return self.get_queryset().last_occurred()

    def in_index(self):
        return self.get_queryset().in_index()


class Incident(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    services = models.ManyToManyField('Service', blank=True,
                                      related_name='incidents',
                                      related_query_name='incident',
                                      verbose_name=_("services"))
    occurred = models.DateTimeField(default=timezone.now, verbose_name=_("occurred"))
    closed = models.BooleanField(default=False)
    objects = IncidentManager()

    def worst_status(self):
        return self.updates.aggregate(worst=models.Max('status'))['worst']

    def updates_by_ctime(self):
        return self.updates.order_by('-created')

    def should_be_closed(self):
        try:
            return self.updates.latest("created").status == 3
        except IncidentUpdate.DoesNotExist:
            return False

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("incident")
        verbose_name_plural = _("incidents")


class IncidentUpdate(TimeStampedModel):
    incident = models.ForeignKey(Incident, related_name='updates',
                                 related_query_name='update',
                                 verbose_name=_("incident"))
    status = models.IntegerField(choices=INCIDENT_STATUSES, verbose_name=_("status"))
    description = models.TextField(verbose_name=_("description"))

    def __str__(self):
        return "Update {} {}".format(self.incident.name, self.modified)

    class Meta:
        verbose_name = _("incident update")
        verbose_name_plural = _("incident updates")


class Maintenance(TimeStampedModel):
    scheduled = models.DateTimeField(verbose_name=_("scheduled"))
    name = models.CharField(max_length=255, verbose_name=_("name"))
    description = models.TextField(verbose_name=_("description"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("maintenance")
        verbose_name_plural = _("maintenances")


@receiver(models.signals.post_save, sender=IncidentUpdate)
@receiver(models.signals.post_delete, sender=IncidentUpdate)
def update_incident_close_field(sender, instance, **kwargs):
    try:
        instance.incident.closed = instance.incident.should_be_closed()
        instance.incident.save()
    except IncidentUpdate.DoesNotExist:
        pass
