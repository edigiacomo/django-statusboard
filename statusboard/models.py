from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from model_utils.models import TimeStampedModel


SERVICE_STATUSES = (
    (0, _('Operational')),
    (1, _('Performance issues')),
    (2, _('Partial outage')),
    (3, _('Major outage')),
)


class ServiceManager(models.Manager):
    def worst_status(self):
        s = self.get_queryset().aggregate(models.Max('status'))["status__max"]
        return s


class Service(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("name"))
    description = models.TextField(verbose_name=_("description"))
    href = models.URLField(blank=True)
    status = models.IntegerField(choices=SERVICE_STATUSES, verbose_name=_("status"))
    groups = models.ManyToManyField('ServiceGroup',
                                    related_name='services',
                                    related_query_name='service',
                                    verbose_name=_("groups"))
    objects = ServiceManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")


class ServiceGroup(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("name"))

    def worst_service(self):
        return self.services.all().latest('status')

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


class IncidentManager(models.Manager):
    def occurred_in_last_n_days(self, days=7):
        threshold = timezone.now() - timezone.timedelta(days=days)
        threshold = timezone.datetime(threshold.year,
                                      threshold.month,
                                      threshold.day)
        qs = self.get_queryset().filter(occurred__gte=threshold)
        return qs


class Incident(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    service = models.ForeignKey('Service', blank=True, null=True,
                                verbose_name=_("service"))
    occurred = models.DateTimeField(default=timezone.now, verbose_name=_("occurred"))
    objects = IncidentManager()

    def worst_status(self):
        return self.updates.aggregate(worst=models.Max('status'))['worst']

    def updates_by_ctime(self):
        return self.updates.order_by('-created')

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
