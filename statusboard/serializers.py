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

from rest_framework import serializers

from .models import (
    Service,
    ServiceGroup,
    Incident,
    IncidentUpdate,
    Maintenance,
)


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "description",
            "href",
            "status",
            "groups",
            "priority",
            "created",
            "modified",
        )


class ServiceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceGroup
        fields = (
            "id",
            "name",
            "collapse",
            "priority",
            "services",
            "created",
            "modified",
        )


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = (
            "id",
            "name",
            "services",
            "occurred",
            "created",
            "modified",
            "updates",
            "closed",
        )
        read_only_fields = ("closed",)


class IncidentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentUpdate
        fields = ("id", "status", "description", "created", "modified")


class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = (
            "id",
            "name",
            "description",
            "created",
            "modified",
            "scheduled",
        )
