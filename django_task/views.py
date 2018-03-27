# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.core import serializers
from django.apps import apps

from .utils import format_datetime
from .models import Task


def tasks_info_api(request):
    # if not request.is_ajax():
    #     raise PermissionDenied
    try:
        json_response = []
        rows = json.loads(request.body.decode('utf-8'))
        for row in rows:
            task_model = apps.get_model(row['model'])
            task_obj = task_model.objects.get(id=row['id'])
            json_response.append(task_obj.as_dict())
        response_status = 200
    except Exception as e:
        json_response = str(e)
        response_status = 404
    return JsonResponse(json_response, status=response_status, safe=False)

