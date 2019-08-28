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

from .models import Incident
from .models import Service
from .models import ServiceGroup
from .models import IncidentUpdate
from .models import Maintenance
from .models import SERVICE_STATUSES


class ServiceGroupForm(forms.ModelForm):
    class Meta:
        model = ServiceGroup
        fields = ['name', 'collapse', 'priority']


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'href', 'description', 'status', 'priority',
                  'groups']


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = ['name', 'description', 'scheduled']


class IncidentForm(forms.ModelForm):

    service_status = forms.ChoiceField(choices=SERVICE_STATUSES,
                                       label='Services status',
                                       required=False)

    class Meta:
        model = Incident
        fields = ['name', 'occurred', 'services', 'service_status']

    def __init__(self, *args, **kwargs):
        """Create an incident form. When the form is populated, the initial
        value of `service_status` is the worst status of the services
        involved."""
        super(IncidentForm, self).__init__(*args, **kwargs)
        if self.instance.pk is not None and self.instance.services.exists():
            last_status = self.instance.services.latest('status').status
            self.fields['service_status'].initial = last_status

    def save(self, commit=True):
        model = super(IncidentForm, self).save(commit=False)
        status = self.cleaned_data['service_status']

        if commit:
            model.save()
            if status is not None:
                self.save_m2m()
                model.services.update(status=status)

        return model


IncidentUpdateFormSet = inlineformset_factory(Incident, IncidentUpdate,
                                              fields=('status', 'description'),
                                              extra=1)
