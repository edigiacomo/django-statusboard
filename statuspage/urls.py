from django.conf.urls import url, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'servicegroups', views.ServiceGroupViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'incidents', views.IncidentViewSet)

app_name = "statuspage"

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^api/(?P<version>v0\.1)/', include(router.urls, namespace="api")),
]
