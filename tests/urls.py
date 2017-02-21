from __future__ import unicode_literals

from django.conf.urls import url, include


urlpatterns = [
    url(r'^statusboard/', include('statusboard.urls', namespace="statusboard")),
]
