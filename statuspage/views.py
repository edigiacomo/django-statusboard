from django.shortcuts import render
from django.http import Http404
from django.core.urlresolvers import reverse_lazy
from django.views.generic.dates import MonthArchiveView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import versioning

from .models import Service, ServiceGroup, Incident
from .serializers import ServiceSerializer, ServiceGroupSerializer, IncidentSerializer
from .forms import IncidentForm


def index(request):
    from django.db.models import Count
    return render(request, "statuspage/index.html", {
        "statusgroups": ServiceGroup.objects.annotate(services_count=Count('service')).filter(services_count__gt=0),
        "worst_service": Service.objects.latest('status'),
        "incidents": Incident.objects.occurred_in_last_n_days(7).order_by('-occurred'),
    })


class IncidentCreateView(CreateView):
    model = Incident
    template_name = "statuspage/incidents/create.html"
    form_class = IncidentForm
    success_url = reverse_lazy('statuspage:index')


class IncidentUpdateView(UpdateView):
    model = Incident
    template_name = "statuspage/incidents/edit.html"
    form_class = IncidentForm
    success_url = reverse_lazy('statuspage:index')


class IncidentMonthArchiveView(MonthArchiveView):
    queryset = Incident.objects.all()
    date_field = "occurred"
    allow_future = False
    month_format = "%m"
    template_name = "statuspage/incidents/archive_month.html"


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
