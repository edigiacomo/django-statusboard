from django.contrib import admin

from .models import Service, ServiceGroup


admin.site.register(Service)
admin.site.register(ServiceGroup)
