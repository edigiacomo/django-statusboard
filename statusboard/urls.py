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

from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'servicegroup', views.ServiceGroupViewSet)
router.register(r'service', views.ServiceViewSet)
router.register(r'incident', views.IncidentViewSet)
router.register(r'incidentupdate', views.IncidentUpdateViewSet)
router.register(r'maintenance', views.MaintenanceViewSet)

app_name = "statusboard"

service_urls = [
    url('^create/$',
        views.ServiceCreate.as_view(),
        name="create"),
    url('^(?P<pk>[0-9]+)/edit/$',
        views.ServiceUpdate.as_view(),
        name="edit"),
    url('^(?P<pk>[0-9]+)/delete/$',
        views.ServiceDelete.as_view(),
        name="delete"),
]

servicegroup_urls = [
    url('^create/$',
        views.ServiceGroupCreate.as_view(),
        name="create"),
    url('^(?P<pk>[0-9]+)/edit/$',
        views.ServiceGroupUpdate.as_view(),
        name="edit"),
    url('^(?P<pk>[0-9]+)/delete/$',
        views.ServiceGroupDelete.as_view(),
        name="delete"),
]

maintenance_urls = [
    url('^create/$',
        views.MaintenanceCreate.as_view(),
        name="create"),
    url('^(?P<pk>[0-9]+)/edit/$',
        views.MaintenanceUpdate.as_view(),
        name="edit"),
    url('^(?P<pk>[0-9]+)/delete/$',
        views.MaintenanceDelete.as_view(),
        name="delete"),
]

incident_urls = [
    url('^archive/$',
        views.incident_archive_index,
        name="archive-index"),
    url('^archive/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$',
        views.IncidentMonthArchiveView.as_view(),
        name="archive-month"),
    url('^create/$',
        views.incident_create,
        name="create"),
    url('^(?P<pk>[0-9]+)/edit/$',
        views.incident_edit,
        name="edit"),
    url('^(?P<pk>[0-9]+)/delete/$',
        views.IncidentDeleteView.as_view(),
        name="delete"),
]

urlpatterns = [
    url(r'^$', views.index, name="index"),
]

urlpatterns += [
    url(r'^login/$', auth_views.LoginView.as_view(
        template_name="statusboard/login.html",
    ), name="login"),
    url(r'^logout/$', auth_views.LogoutView.as_view(
        template_name="statusboard/login.html",
    ), name="logout"),
]

urlpatterns += [
    url(r'^service/', include((service_urls, "service"))),
    url(r'^servicegroup/', include((servicegroup_urls, "servicegroup"))),
    url(r'^incident/', include((incident_urls, "incident"))),
    url(r'^maintenance/', include((maintenance_urls, "maintenance"))),
    url(r'^api/(?P<version>(v0\.1))/', include((router.urls, "api"))),
]
