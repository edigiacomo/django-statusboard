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
        fields = ['name', 'href', 'description', 'status', 'priority', 'groups']


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
            self.fields['service_status'].initial = self.instance.services.latest('status').status

    def save(self, commit=True):
        model = super(IncidentForm, self).save(commit=False)
        status = self.cleaned_data['service_status']

        if commit:
            model.save()

        if model.pk is not None and status is not None:
            self.save_m2m()
            model.services.update(status=status)

        return model


IncidentUpdateFormSet = inlineformset_factory(Incident, IncidentUpdate,
                                              fields=('status', 'description'),
                                              extra=1)
