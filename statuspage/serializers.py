from rest_framework import serializers

from .models import Service, ServiceGroup, Incident


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'description', 'href', 'status', 'groups',
                  'created', 'modified')
        extra_kwargs = {
            'groups': {
                'view_name': 'statuspage:api:servicegroup-detail',
            }
        }


class ServiceGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ServiceGroup
        fields = ('id', 'name', 'services', 'created', 'modified')
        extra_kwargs = {
            'services': {
                'view_name': 'statuspage:api:service-detail',
            }
        }


class IncidentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Incident
        fields = ('id', 'name', 'service', 'status', 'description', 'occurred')
        extra_kwargs = {
            'service': {
                'view_name': 'statuspage:api:service-detail',
            }
        }
