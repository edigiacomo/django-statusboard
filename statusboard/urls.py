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
    url(r'^service/', include(service_urls, namespace="service")),
    url(r'^servicegroup/', include(servicegroup_urls, namespace="servicegroup")),
    url(r'^incident/', include(incident_urls, namespace="incident")),
    url(r'^maintenance/', include(maintenance_urls, namespace="maintenance")),
    url(r'^api/(?P<version>v0\.1)/', include(router.urls, namespace="api")),
    url(r'^login/$', auth_views.login, {
        "template_name": "statusboard/login.html",
    }, name="login"),
    url(r'^logout/$', auth_views.logout, {
        "template_name": "statusboard/login.html",
    }, name="logout"),
]
