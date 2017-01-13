from rest_framework import serializers

from .models import Service, ServiceGroup


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
