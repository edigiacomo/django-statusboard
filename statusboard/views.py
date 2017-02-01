from django.shortcuts import render
from django.http import Http404
from django.views.generic.dates import MonthArchiveView

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import versioning

from .models import Service, ServiceGroup, Incident, IncidentUpdate
from .serializers import ServiceSerializer, ServiceGroupSerializer, IncidentSerializer, IncidentUpdateSerializer


def index(request):
    from django.db.models import Count
    return render(request, "statusboard/index.html", {
        "statusgroups": ServiceGroup.objects.annotate(services_count=Count('service')).filter(services_count__gt=0),
        "worst_status": Service.objects.worst_status(),
        "incidents": Incident.objects.occurred_in_last_n_days(7).order_by('-modified'),
    })


class IncidentMonthArchiveView(MonthArchiveView):
    queryset = Incident.objects.all()
    date_field = "occurred"
    allow_future = False
    month_format = "%m"
    template_name = "statusboard/incidents/archive_month.html"


    def get_year(self):
        try:
            return super(IncidentMonthArchiveView, self).get_year()
        except Http404:
            return str(self.get_queryset().latest(self.date_field).occurred.year)

    def get_month(self):
        try:
            return super(IncidentMonthArchiveView, self).get_month()
        except Http404:
            return str(self.get_queryset().latest(self.date_field).occurred.month)


class ServiceGroupViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceGroupSerializer
    queryset = ServiceGroup.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    versioning_class = versioning.URLPathVersioning


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    versioning_class = versioning.URLPathVersioning


class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    queryset = Incident.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    versioning_class = versioning.URLPathVersioning


class IncidentUpdateViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentUpdateSerializer
    queryset = IncidentUpdate.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    versioning_class = versioning.URLPathVersioning
