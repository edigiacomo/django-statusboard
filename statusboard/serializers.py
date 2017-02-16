from rest_framework import serializers

from .models import Service, ServiceGroup, Incident, IncidentUpdate, Maintenance


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'description', 'href', 'status', 'groups',
                  'created', 'modified')


class ServiceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceGroup
        fields = ('id', 'name', 'collapse', 'services', 'created', 'modified')


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ('id', 'name', 'service', 'occurred', 'created', 'modified',
                  'updates')


class IncidentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentUpdate
        fields = ('id', 'status', 'description', 'created', 'modified')


class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = ('id', 'name', 'description', 'created', 'modified',
                  'scheduled')
