from django.db import models
from django.utils import timezone

from model_utils.models import TimeStampedModel


SERVICE_STATUSES = (
    (0, 'Operational'),
    (1, 'Performance issues'),
    (2, 'Partial outage'),
    (3, 'Major outage'),
)


class Service(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    href = models.URLField(blank=True)
    status = models.IntegerField(choices=SERVICE_STATUSES)
    groups = models.ManyToManyField('ServiceGroup', blank=True,
                                    related_name='services',
                                    related_query_name='service')

    def __str__(self):
        return self.name


class ServiceGroup(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)

    def worst_service(self):
        return self.services.all().latest('status')

    def __str__(self):
        return self.name


INCIDENT_STATUSES = (
    (0, "Investigating"),
    (1, "Identified"),
    (2, "Watching"),
    (3, "Fixed"),
)


class Incident(TimeStampedModel):
    name = models.CharField(max_length=255)
    service = models.ForeignKey('Service', blank=True, null=True)
    status = models.IntegerField(choices=INCIDENT_STATUSES)
    description = models.TextField()
    occurred = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
