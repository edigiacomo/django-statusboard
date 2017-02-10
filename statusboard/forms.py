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
        fields = ['name']


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'href', 'description', 'status', 'groups']


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = ['name', 'description', 'scheduled']


class IncidentForm(forms.ModelForm):

    service_status = forms.IntegerField(
        label='Service status', widget=forms.Select(choices=SERVICE_STATUSES),
    )

    class Meta:
        model = Incident
        fields = ['name', 'occurred', 'service', 'service_status']

    def __init__(self, *args, **kwargs):
        super(IncidentForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.service:
            self.fields['service_status'].initial = self.instance.service.status

    def save(self, commit=True):
        model = super(IncidentForm, self).save(commit=False)
        status = self.cleaned_data['service_status']
        if status:
            if model.service:
                model.service.status = status
                model.service.save()
            else:
                # model.service = Service()
                pass

        if commit:
            model.save()

        return model


IncidentUpdateFormSet = inlineformset_factory(Incident, IncidentUpdate,
                                              fields=('status', 'description'),
                                              extra=1)
