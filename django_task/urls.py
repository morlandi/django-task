from __future__ import unicode_literals
from django.conf.urls import include, url
from django.contrib import admin
from .views import tasks_info_api


urlpatterns = [
    url(r'^info/$', tasks_info_api, name="django_task_info"),
]
