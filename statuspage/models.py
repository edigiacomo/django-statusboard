from django.db import models
from model_utils.models import TimeStampedModel


STATUSES = (
    (0, 'Operational'),
    (1, 'Performance issues'),
    (2, 'Partial outage'),
    (3, 'Major outage'),
)


class Service(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    href = models.URLField(blank=True)
    status = models.IntegerField(choices=STATUSES)
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
