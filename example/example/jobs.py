from __future__ import print_function
import time
import redis
import logging
from django.conf import settings
from .models import CountBeansTask
from .models import SendEmailTask
from rq import get_current_job
from django_rq import job


@job(CountBeansTask.TASK_QUEUE)
def count_beans(task_id):

    task = None
    result = 'SUCCESS'
    failure_reason = ''

    try:

        # this raises a "Could not resolve a Redis connection" exception in sync mode
        #job = get_current_job()
        job = get_current_job(connection=redis.Redis.from_url(settings.REDIS_URL))
        #task = CountBeansTask.objects.get(id=task_id)
        task = CountBeansTask.get_task_from_id(task_id)
        task.set_status(status='STARTED', job_id=job.get_id())

        params = task.retrieve_params_as_dict()
        num_beans = params['num_beans']

        for i in range(0, num_beans):
            time.sleep(0.01)
            task.set_progress((i + 1) * 100 / num_beans, step=10)

    except Exception as e:
        if task:
            task.log(logging.ERROR, str(e))
        result = 'FAILURE'
        failure_reason = str(e)

    finally:
        if task:
            task.set_status(status=result, failure_reason=failure_reason)


@job(SendEmailTask.TASK_QUEUE)
def send_email(task_id):

    task = None
    result = 'SUCCESS'
    failure_reason = ''

    try:

        # this raises a "Could not resolve a Redis connection" exception in sync mode
        #job = get_current_job()
        job = get_current_job(connection=redis.Redis.from_url(settings.REDIS_URL))
        #task = SendEmailTask.objects.get(id=task_id)
        task = SendEmailTask.get_task_from_id(task_id)
        task.set_status(status='STARTED', job_id=job.get_id())

        params = task.retrieve_params_as_dict()

        recipient_list = params['recipients'].split()
        sender = params['sender'].strip()
        subject = params['subject'].strip()
        message = params['message']

        from django.core.mail import send_mail
        send_mail(subject, message, sender, recipient_list)

    except Exception as e:
        if task:
            task.log(logging.ERROR, str(e))
        result = 'FAILURE'
        failure_reason = str(e)

    finally:
        if task:
            task.set_status(status=result, failure_reason=failure_reason)
