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

from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import Incident
from .models import Service
from .models import ServiceGroup
from .models import IncidentUpdate
from .models import Maintenance
from .models import SERVICE_STATUSES


# DateTimeLocalInput and DateTimeLocalField classes were copied from https://stackoverflow.com/a/69965027 hence they are
# distributed under CC BY-SA 4.0 (see https://stackoverflow.com/help/licensing).


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"


class DateTimeLocalField(forms.DateTimeField):
    # Set DATETIME_INPUT_FORMATS here because, if USE_L10N
    # is True, the locale-dictated format will be applied
    # instead of settings.DATETIME_INPUT_FORMATS.
    # See also:
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Date_and_time_formats

    input_formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M",
    ]
    widget = DateTimeLocalInput(format="%Y-%m-%dT%H:%M")


class ServiceGroupForm(forms.ModelForm):
    class Meta:
        model = ServiceGroup
        fields = ["name", "collapse", "priority"]


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            "name",
            "href",
            "description",
            "status",
            "priority",
            "groups",
        ]


class MaintenanceForm(forms.ModelForm):
    scheduled = DateTimeLocalField()

    class Meta:
        model = Maintenance
        fields = ["name", "description", "scheduled"]


class IncidentForm(forms.ModelForm):
    service_status = forms.ChoiceField(
        choices=tuple([("", "---------")] + list(SERVICE_STATUSES)),
        label=_("Services status"),
        help_text=_("Update the status of involved services (an empty value means that they will be left unaltered)"),
        required=False,
    )
    occurred = DateTimeLocalField()

    class Meta:
        model = Incident
        fields = ["name", "occurred", "services", "service_status"]

    def __init__(self, *args, **kwargs):
        super(IncidentForm, self).__init__(*args, **kwargs)
        self.fields["services"].queryset = Service.objects.order_by("name")

    def save(self, commit=True):
        model = super(IncidentForm, self).save(commit=False)
        status = self.cleaned_data["service_status"]

        if commit:
            model.save()
            self.save_m2m()
            if status not in (None, ""):
                model.services.update(status=status)

        return model


IncidentUpdateFormSet = inlineformset_factory(Incident, IncidentUpdate, fields=("status", "description"), extra=1)
