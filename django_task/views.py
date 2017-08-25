# -*- encoding: utf-8 -*-
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.core import serializers

from .utils import format_datetime
from .models import Task


def tasks_info_api(request):
    # if not request.is_ajax():
    #     raise PermissionDenied
    try:
        ids = request.GET.getlist('ids[]')
        tasks = Task.objects.filter(id__in=ids)
        json_response = [task.get_child().as_dict() for task in tasks]
        response_status = 200
    except Exception as e:
        json_response = str(e)
        response_status = 404
    return JsonResponse(json_response, status=response_status, safe=False)

