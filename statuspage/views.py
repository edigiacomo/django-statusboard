from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import permissions

from .models import Service, ServiceGroup
from .serializers import ServiceSerializer, ServiceGroupSerializer


def index(request):
    return render(request, "statuspage/index.html", {
        "statusgroups": ServiceGroup.objects.all(),
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
