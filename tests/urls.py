from django.urls import include, path


urlpatterns = [
    path('', include('django_task.urls', namespace='django_task')),
]
