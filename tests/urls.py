# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

try:
    from django.urls import url, include
except:
    from django.conf.urls import url, include


urlpatterns = [
    url(r'^', include('django_task.urls', namespace='django_task')),
]
