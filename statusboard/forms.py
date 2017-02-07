from django import forms

from .models import Incident
from .models import Service
from .models import SERVICE_STATUSES


class IncidentForm(forms.ModelForm):

    service_status = forms.IntegerField(
        label='service_status', widget=forms.Select(choices=SERVICE_STATUSES),
    )

    class Meta:
        model = Incident
        fields = ['name', 'service', 'occurred', 'service_status']
