from django.urls import path
# TODO: When dropping support for Django < 2.0, use this instead:
#from django.urls import path

from django.contrib import admin
from . import views

app_name = "django_task"

urlpatterns = [
    path('info/', views.tasks_info_api, name="django_tasks_info"),
    path('add/', views.task_add_api, name="django_task_add"),
    path('<str:app_label>/<str:model_name>/<uuid:pk>/run/<int:is_async>/', views.task_run_api, name="django_task_run"),
    path('<str:app_label>/<str:model_name>/<uuid:pk>/run/', views.task_run_api, name="django_task_run"),
]
