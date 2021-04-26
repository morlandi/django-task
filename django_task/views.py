# -*- encoding: utf-8 -*-
import json
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.core import serializers
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.http import HttpResponse

from .utils import format_datetime
from .utils import get_object_by_uuid_or_404


def tasks_info_api(request):
    """
    Retrieve informations about a list of existing tasks.

    Sample usage (javascript):

        var tasks = [{
            id: 'c50bf040-a886-4aed-bf41-4ae794db0941',
            model: 'tasks.devicetesttask'
        }, {
            id: 'e567c651-c8d5-4dc7-9cbf-860988f55022',
            model: 'tasks.devicetesttask'
        }];

        $.ajax({
            url: '/django_task/info/',
            data: JSON.stringify(tasks),
            cache: false,
            type: 'post',
            dataType: 'json',
            headers: {'X-CSRFToken': getCookie('csrftoken')}
        }).done(function(data) {
            console.log('data: %o', data);
        });

    Result:

    [
      {
        "id": "c50bf040-a886-4aed-bf41-4ae794db0941",
        "created_on": "2018-10-11T17:45:14.399491+00:00",
        "created_on_display": "10/11/2018 19:45:14",
        "created_by": "4f943f0b-f5a3-4fd8-bb2e-451d2be107e2",
        "started_on": null,
        "started_on_display": "",
        "completed_on": null,
        "completed_on_display": "",
        "job_id": "",
        "status": "PENDING",
        "status_display": "<div class=\"task_status\" data-task-model=\"tasks.devicetesttask\" data-task-id=\"c50bf040-a886-4aed-bf41-4ae794db0941\" data-task-status=\"PENDING\" data-task-complete=\"0\">PENDING</div>",
        "log_link_display": "",
        "failure_reason": "",
        "progress": null,
        "progress_display": "-",
        "completed": false,
        "duration": null,
        "duration_display": "",
        "extra_fields": {
        }
      },
      ...
    ]
    """


    # if not request.is_ajax():
    #     raise PermissionDenied
    try:
        json_response = []
        rows = json.loads(request.body.decode('utf-8'))

        # for row in rows:
        #     task_model = apps.get_model(row['model'])
        #     task_obj = task_model.objects.get(id=row['id'])
        #     json_response.append(task_obj.as_dict())

        # 2019-08-07 optimization
        # TODO: are we still using "extra_fields" somewhere ? ... if so, we
        # should either add them to the "columns" list, or remove only()

        columns = ['id', 'created_on', 'created_by', 'started_on', 'completed_on',
            'job_id', 'status', 'failure_reason', 'progress', 'log_text', ]

        if len(rows) > 0:
            distinct_models = list(set([row['model'] for row in rows]))
            if len(distinct_models) == 1:
                # if a single model is involved, as normally happens,
                # we can use a single query
                task_model = apps.get_model(distinct_models[0])
                ids = [row['id'] for row in rows]
                queryset = task_model.objects.filter(id__in=ids).select_related('created_by').only(*columns)
                for task_obj in queryset:
                    json_response.append(task_obj.as_dict())
            else:
                for row in rows:
                    task_model = apps.get_model(row['model'])
                    queryset = task_model.objects.filter(id=row['id']).select_related('created_by').only(*columns)
                    task_obj = queryset[0]
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

    Returns the id of the new task.


    Sample usage (javescript):

        function exportAcquisition(object_id) {
            if (confirm('Do you want to export data ?')) {

                var url = '/django_task/add/';
                var data = JSON.stringify({
                    'task-model': 'tasks.exportdatatask',
                    'source': 'backend.acquisition',
                    'object_id': object_id
                });

                $.ajax({
                    type: 'POST',
                    url: url,
                    data: data,
                    cache: false,
                    crossDomain: true,
                    dataType: 'json',
                    headers: {'X-CSRFToken': getCookie('csrftoken')}
                }).done(function(data) {
                    console.log('data: %o', data);
                    alert('New task created: "' + data.task_id + '"');
                }).fail(function(jqXHR, textStatus, errorThrown) {
                    console.log('ERROR: ' + jqXHR.responseText);
                    alert(errorThrown);
                });
            }
            return;
        }
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


@login_required
def task_run_api(request, app_label, model_name, pk, is_async=1):
    """
    Schedule execution of specified task;
    Returns job.id or throws error (400)

    Sample usage (javescript):

    var task_id = 'c50bf040-a886-4aed-bf41-4ae794db0941';

    $.ajax({
        url: sprintf('/django_task/tasks/devicetesttask/%s/run/', task_id),
        cache: false,
        type: 'get'
    }).done(function(data) {
        console.log('data: %o', data);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        display_server_error(jqXHR.responseText);
    });
    """

    try:
        model = apps.get_model(app_label, model_name)
        task = get_object_by_uuid_or_404(model, str(pk))
        is_async = bool(is_async)
        job = task.run(is_async, request)
        content = str(job.id)
        response_status = 200
    except Exception as e:
        content = str(e)
        response_status = 400

    return HttpResponse(content=content, status=response_status)
