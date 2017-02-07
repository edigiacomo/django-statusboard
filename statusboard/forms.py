from django import forms

from .models import Incident
from .models import Service


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['name', 'service', 'occurred']
