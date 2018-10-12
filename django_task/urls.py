from __future__ import unicode_literals

from django.conf.urls import url
# TODO: When dropping support for Django < 2.0, use this instead:
#from django.urls import path

from django.contrib import admin
from . import views

app_name = "django_task"

urlpatterns = [
    url(r'^info/$', views.tasks_info_api, name="django_task_info"),
    url(r'^add/$', views.task_add_api, name="django_task_add"),
    url(r'^(?P<app_label>[\w\-]+)/(?P<model_name>[\w\-]+)/(?P<pk>[0-9a-f-]+)/run/$', views.task_run_api, name="django_task_run"),
    url(r'^(?P<app_label>[\w\-]+)/(?P<model_name>[\w\-]+)/(?P<pk>[0-9a-f-]+)/run/(?P<is_async>\d+)$', views.task_run_api, name="django_task_run"),

    # TODO: When dropping support for Django < 2.0, use this instead:
    # path('info/', views.tasks_info_api, name="django_tasks_info"),
    # path('add/', views.task_add_api, name="django_task_add"),
    # path('<str:app_label>/<str:model_name>/<uuid:pk>/run/<int:is_async>/', views.task_run_api, name="django_task_run"),
    # path('<str:app_label>/<str:model_name>/<uuid:pk>/run/', views.task_run_api, name="django_task_run"),
]
