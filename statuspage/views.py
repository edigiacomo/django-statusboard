from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import permissions

from .models import Service, ServiceGroup
from .serializers import ServiceSerializer, ServiceGroupSerializer


def index(request):
    from django.db.models import Count
    return render(request, "statuspage/index.html", {
        "statusgroups": ServiceGroup.objects.annotate(services_count=Count('service')).filter(services_count__gt=0),
        "worst_service": Service.objects.latest('status'),
    })


class ServiceGroupViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceGroupSerializer
    queryset = ServiceGroup.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
