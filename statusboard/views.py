from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic.dates import MonthArchiveView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.db import transaction

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import versioning

from .models import Service, ServiceGroup, Incident, IncidentUpdate
from .serializers import ServiceSerializer, ServiceGroupSerializer, IncidentSerializer, IncidentUpdateSerializer
from .forms import IncidentForm, IncidentUpdateFormSet


def index(request):
    from django.db.models import Count
    return render(request, "statusboard/index.html", {
        "statusgroups": ServiceGroup.objects.annotate(services_count=Count('service')).filter(services_count__gt=0),
        "worst_status": Service.objects.worst_status(),
        "incidents": Incident.objects.occurred_in_last_n_days(7).order_by('-modified'),
    })


def incident_create(request):
    if request.POST:
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident_updates = IncidentUpdateFormSet(request.POST, instance=incident)
            if incident_updates.is_valid():
                incident.save()
                incident_updates.save()
                return HttpResponseRedirect(reverse('statusboard:index'))
    else:
        form = IncidentForm()
        incident_updates = IncidentUpdateFormSet()

    return render(request, "statusboard/incidents/create.html", {
        "form": form,
        "incident_updates": incident_updates,
    })


def incident_update(request, pk):
    incident = Incident.objects.get(pk=pk)

    if request.POST:
        form = IncidentForm(request.POST or None, instance=incident)
        if form.is_valid():
            incident = form.save(commit=False)
            incident_updates = IncidentUpdateFormSet(request.POST, request.FILES, instance=incident)
            if incident_updates.is_valid():
                incident.save()
                incident_updates.save()
                return HttpResponseRedirect(reverse('statusboard:index'))

    else:
        form = IncidentForm(instance=incident)
        incident_updates = IncidentUpdateFormSet(instance=incident)

    return render(request, "statusboard/incidents/edit.html", {
        "form": form,
        "incident_updates": incident_updates,
    })


class IncidentUpdateView(UpdateView):
    model = Incident
    template_name = "statusboard/incidents/edit.html"
    form_class = IncidentForm
    success_url = reverse_lazy('statusboard:index')

    def get_context_data(self, **kwargs):
        from .forms import IncidentUpdateFormSet
        data = super(IncidentUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['incident_updates'] = IncidentUpdateFormSet(self.request.POST, instance=self.get_object())
        else:
            data['incident_updates'] = IncidentUpdateFormSet(instance=self.get_object())

        return data

    def form_valid(self, form):
        context = self.get_context_data()
        incident_updates = context['incident_updates']
        with transaction.atomic():
            self.object = form.save()
            if incident_updates.is_valid():
                incident_updates.instance = self.object
                incident_updates.save()

        return super(IncidentCreateView, self).form_valid(form)


class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = "statusboard/incidents/confirm_delete.html"
    success_url = reverse_lazy('statusboard:index')


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
