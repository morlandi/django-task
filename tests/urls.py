# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from django_task.urls import urlpatterns as django_task_urls

urlpatterns = [
    url(r'^', include(django_task_urls, namespace='django_task')),
]
