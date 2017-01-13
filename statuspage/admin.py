from django.contrib import admin

from .models import Service, ServiceGroup, Incident


admin.site.register(Service)
admin.site.register(ServiceGroup)
admin.site.register(Incident)
