from rest_framework import serializers

from .models import Service, ServiceGroup, Incident


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'description', 'href', 'status', 'groups',
                  'created', 'modified')


class ServiceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceGroup
        fields = ('id', 'name', 'services', 'created', 'modified')


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ('id', 'name', 'service', 'status', 'description', 'occurred')
