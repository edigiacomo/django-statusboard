from __future__ import unicode_literals

from django.contrib import admin

from .models import Service, ServiceGroup, Incident, IncidentUpdate, Maintenance


class IncidentUpdateInline(admin.TabularInline):
    model = IncidentUpdate
    ordering = ["created"]


class IncidentAdmin(admin.ModelAdmin):
    inlines = [IncidentUpdateInline]


admin.site.register(Service)
admin.site.register(ServiceGroup)
admin.site.register(Incident, IncidentAdmin)
admin.site.register(Maintenance)
