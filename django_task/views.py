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


def task_add_api(request):
    """
    Create and run a new task based on specified parameters.
    Expected parameters:
        'task-model' = "<app_name>.<model_name>"
        ... task parameters ...

    Returns the id of the new task
    """

    if request.method != 'POST' or not request.user.is_authenticated:
        raise PermissionDenied
    try:

        json_response = {}

        parameters = json.loads(request.body.decode('utf-8'))

        # Retrieve model
        task_model = parameters.pop('task-model')
        Model = apps.get_model(task_model)

        # Remove m2m values
        m2m_fields = {}
        for field in Model._meta.many_to_many:
            field_name = field.attname
            if field_name in parameters:
                m2m_fields[field_name] = parameters.pop(field_name)

        # Create new task
        parameters.update({'created_by': request.user, })
        task = Model.objects.create(**parameters)

        # Add m2m values, if any
        dirty = False
        for field_name, values in m2m_fields.items():
            if values:
                getattr(task, field_name).set(values)
                dirty = True
        if dirty:
            task.save()

        json_response['task_id'] = str(task.id)
        task.run(is_async=True)

        response_status = 200

    except Exception as e:
        json_response = str(e)
        response_status = 400

    return JsonResponse(json_response, status=response_status, safe=False)
