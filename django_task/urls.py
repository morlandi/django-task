from __future__ import unicode_literals
from django.conf.urls import include, url
from django.contrib import admin
from . import views

app_name = "django_task"

urlpatterns = [
    url(r'^info/$', views.tasks_info_api, name="django_task_info"),
    url(r'^add/$', views.task_add_api, name="django_task_add"),
]
