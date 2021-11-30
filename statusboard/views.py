# Copyright (C) 2017 Emanuele Di Giacomo <emanuele@digiacomo.cc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic.dates import MonthArchiveView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.utils import timezone
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import versioning

from .models import (
    Service,
    ServiceGroup,
    Incident,
    IncidentUpdate,
    Maintenance,
)
from .serializers import (
    ServiceSerializer,
    ServiceGroupSerializer,
    IncidentSerializer,
    IncidentUpdateSerializer,
    MaintenanceSerializer,
)
from .forms import (
    IncidentForm,
    IncidentUpdateFormSet,
    ServiceGroupForm,
    ServiceForm,
    MaintenanceForm,
)
from .settings import statusconf


def index(request):
    worst_status = Service.objects.worst_status()
    return render(
        request,
        "statusboard/index.html",
        {
            "servicegroups": ServiceGroup.objects.priority_sorted(),
            "uncategorized": Service.objects.uncategorized(),
            "worst_status": worst_status,
            "incidents": Incident.objects.in_index().order_by("-occurred"),
            "maintenances": Maintenance.objects.filter(
                scheduled__gt=timezone.now()
            ).order_by("-scheduled"),
            "auto_refresh": statusconf.AUTO_REFRESH_INDEX_SECONDS,
            "favicon": statusconf.FAVICON_INDEX_DICT.get(
                worst_status,
                statusconf.FAVICON_DEFAULT,
            ),
        },
    )


class ServiceGroupCreate(PermissionRequiredMixin, CreateView):
    model = ServiceGroup
    form_class = ServiceGroupForm
    template_name = "statusboard/servicegroup/create.html"
    success_url = reverse_lazy("statusboard:index")
    permission_required = "statusboard.create_servicegroup"


class ServiceGroupUpdate(PermissionRequiredMixin, UpdateView):
    model = ServiceGroup
    form_class = ServiceGroupForm
    template_name = "statusboard/servicegroup/edit.html"
    success_url = reverse_lazy("statusboard:index")
    permission_required = "statusboard.change_servicegroup"


class ServiceGroupDelete(PermissionRequiredMixin, DeleteView):
    model = ServiceGroup
    template_name = "statusboard/servicegroup/confirm_delete.html"
    success_url = reverse_lazy("statusboard:index")
    permission_required = "statusboard.delete_servicegroup"


class ServiceCreate(PermissionRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "statusboard/service/create.html"
    success_url = reverse_lazy("statusboard:index")
    permission_required = "statusboard.add_service"


class ServiceUpdate(PermissionRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "statusboard/service/edit.html"
    success_url = reverse_lazy("statusboard:index")
    permission_required = "statusboard.change_service"


class ServiceDelete(PermissionRequiredMixin, DeleteView):
    model = Service
    template_name = "statusboard/service/confirm_delete.html"
    success_url = reverse_lazy("statusboard:index")
    permission_required = "statusboard.delete_service"


class MaintenanceCreate(PermissionRequiredMixin, CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = "statusboard/maintenance/create.html"
    success_url = reverse_lazy("statusboard:index")
    permission_required = "statusboard.create_maintenance"


class MaintenanceUpdate(PermissionRequiredMixin, UpdateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = "statusboard/maintenance/edit.html"
    success_url = reverse_lazy("statusboard:index")
    permission_required = "statusboard.change_maintenance"


class MaintenanceDelete(PermissionRequiredMixin, DeleteView):
    model = Maintenance
    template_name = "statusboard/maintenance/confirm_delete.html"
    success_url = reverse_lazy("statusboard:index")
    permission_required = "statusboard.delete_maintenance"


@permission_required("statusboard.create_incident")
def incident_create(request):
    form = IncidentForm()
    incident_updates = IncidentUpdateFormSet()
    if request.POST:
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident_updates = IncidentUpdateFormSet(
                request.POST, instance=incident
            )
            if incident_updates.is_valid():
                form.save()
                incident_updates.save()
                return HttpResponseRedirect(reverse("statusboard:index"))

    return render(
        request,
        "statusboard/incident/create.html",
        {
            "form": form,
            "incident_updates": incident_updates,
        },
    )


@permission_required("statusboard.change_incident")
def incident_edit(request, pk):
    incident = Incident.objects.get(pk=pk)
    form = IncidentForm(instance=incident)
    incident_updates = IncidentUpdateFormSet(instance=incident)

    if request.POST:
        form = IncidentForm(request.POST or None, instance=incident)
        if form.is_valid():
            incident = form.save(commit=False)
            incident_updates = IncidentUpdateFormSet(
                request.POST, request.FILES, instance=incident
            )
            if incident_updates.is_valid():
                form.save()
                incident_updates.save()
                return HttpResponseRedirect(reverse("statusboard:index"))

    return render(
        request,
        "statusboard/incident/edit.html",
        {
            "form": form,
            "incident_updates": incident_updates,
        },
    )


class IncidentDeleteView(PermissionRequiredMixin, DeleteView):
    model = Incident
    template_name = "statusboard/incident/confirm_delete.html"
    success_url = reverse_lazy("statusboard:index")
    permission_required = "statusboard.delete_incident"


def incident_archive_index(request):
    try:
        dt = Incident.objects.latest("occurred").occurred
        return redirect(
            "statusboard:incident:archive-month", year=dt.year, month=dt.month
        )
    except Incident.DoesNotExist:
        return render(request, "statusboard/incident/archive_month_empty.html")


class IncidentMonthArchiveView(MonthArchiveView):
    queryset = Incident.objects.all().order_by("-occurred")
    date_field = "occurred"
    allow_future = False
    month_format = "%m"
    template_name = "statusboard/incident/archive_month.html"


class ServiceGroupViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceGroupSerializer
    queryset = ServiceGroup.objects.all()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    versioning_class = versioning.URLPathVersioning


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    versioning_class = versioning.URLPathVersioning


class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    queryset = Incident.objects.all()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    versioning_class = versioning.URLPathVersioning


class IncidentUpdateViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentUpdateSerializer
    queryset = IncidentUpdate.objects.all()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    versioning_class = versioning.URLPathVersioning


class MaintenanceViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceSerializer
    queryset = Maintenance.objects.all()
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    versioning_class = versioning.URLPathVersioning
