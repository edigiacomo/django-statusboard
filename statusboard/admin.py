# Copyright (C) 2017 Emanuele Di Giacomo <emanuele@digiacomo.cc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from django.contrib import admin

from .models import (
    Service,
    ServiceGroup,
    Incident,
    IncidentUpdate,
    Maintenance,
)


class IncidentUpdateInline(admin.TabularInline):
    model = IncidentUpdate
    ordering = ["created"]


class IncidentAdmin(admin.ModelAdmin):
    inlines = [IncidentUpdateInline]


admin.site.register(Service)
admin.site.register(ServiceGroup)
admin.site.register(Incident, IncidentAdmin)
admin.site.register(Maintenance)
