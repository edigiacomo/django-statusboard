from django.conf.urls import url, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'servicegroups', views.ServiceGroupViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'incidents', views.IncidentViewSet)
router.register(r'incidentupdates', views.IncidentUpdateViewSet)

app_name = "statusboard"

incident_urls = [
    url('^archive/$',
        views.IncidentMonthArchiveView.as_view(),
        name="archive-index"),
    url('^archive/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$',
        views.IncidentMonthArchiveView.as_view(),
        name="archive-month"),
]

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^incidents/', include(incident_urls, namespace="incident")),
    url(r'^api/(?P<version>v0\.1)/', include(router.urls, namespace="api")),
]
