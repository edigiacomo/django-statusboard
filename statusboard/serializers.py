from __future__ import unicode_literals

from rest_framework import serializers

from .models import Service, ServiceGroup, Incident, IncidentUpdate, Maintenance


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'description', 'href', 'status', 'groups',
                  'priority', 'created', 'modified')


class ServiceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceGroup
        fields = ('id', 'name', 'collapse', 'priority', 'services', 'created', 'modified')


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ('id', 'name', 'services', 'occurred', 'created', 'modified',
                  'updates', 'closed')
        read_only_fields = ('closed',)


class IncidentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentUpdate
        fields = ('id', 'status', 'description', 'created', 'modified')


class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = ('id', 'name', 'description', 'created', 'modified',
                  'scheduled')
