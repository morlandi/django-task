"""example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin
from django.shortcuts import redirect
from django.conf import settings

admin.site.enable_nav_sidebar = False

urlpatterns = [
    path('', lambda x: redirect('/admin/')),
    path('admin/', admin.site.urls),
    path('django_task/', include('django_task.urls', namespace='django_task')),
]

if settings.USE_DJANGO_RQ:
    urlpatterns += [
        path('django-rq/', include('django_rq.urls')),
    ]
