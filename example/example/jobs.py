from __future__ import print_function
import time
import redis
import logging
import traceback
from django.conf import settings
from .models import CountBeansTask
from .models import SendEmailTask
from django_task.job import Job
from rq import get_current_job


class CountBeansJob(Job):

    @staticmethod
    def execute(job, task):
        params = task.retrieve_params_as_dict()
        num_beans = params['num_beans']
        for i in range(0, num_beans):
            time.sleep(0.01)
            task.set_progress((i + 1) * 100 / num_beans, step=10)


# def count_beans(task_id):

#     task = None
#     result = 'SUCCESS'
#     failure_reason = ''

#     try:

#         # this raises a "Could not resolve a Redis connection" exception in sync mode
#         #job = get_current_job()
#         job = get_current_job(connection=redis.Redis.from_url(settings.REDIS_URL))
#         #task = CountBeansTask.objects.get(id=task_id)
#         task = CountBeansTask.get_task_from_id(task_id)
#         task.set_status(status='STARTED', job_id=job.get_id())

#         params = task.retrieve_params_as_dict()
#         num_beans = params['num_beans']

#         for i in range(0, num_beans):
#             time.sleep(0.01)
#             task.set_progress((i + 1) * 100 / num_beans, step=10)

#     except Exception as e:
#         if task:
#             task.log(logging.ERROR, str(e))
#             task.log(logging.ERROR, traceback.format_exc())
#         result = 'FAILURE'
#         failure_reason = str(e)

#     finally:
#         if task:
#             task.set_status(status=result, failure_reason=failure_reason)



class SendEmailJob(Job):

    @staticmethod
    def execute(job, task):
        params = task.retrieve_params_as_dict()
        recipient_list = params['recipients'].split()
        sender = params['sender'].strip()
        subject = params['subject'].strip()
        message = params['message']
        from django.core.mail import send_mail
        send_mail(subject, message, sender, recipient_list)


# def send_email(task_id):

#     task = None
#     result = 'SUCCESS'
#     failure_reason = ''

#     try:

#         # this raises a "Could not resolve a Redis connection" exception in sync mode
#         #job = get_current_job()
#         job = get_current_job(connection=redis.Redis.from_url(settings.REDIS_URL))
#         #task = SendEmailTask.objects.get(id=task_id)
#         task = SendEmailTask.get_task_from_id(task_id)
#         task.set_status(status='STARTED', job_id=job.get_id())

#         params = task.retrieve_params_as_dict()

#         recipient_list = params['recipients'].split()
#         sender = params['sender'].strip()
#         subject = params['subject'].strip()
#         message = params['message']

#         from django.core.mail import send_mail
#         send_mail(subject, message, sender, recipient_list)

#     except Exception as e:
#         if task:
#             task.log(logging.ERROR, str(e))
#             task.log(logging.ERROR, traceback.format_exc())
#         result = 'FAILURE'
#         failure_reason = str(e)

#     finally:
#         if task:
#             task.set_status(status=result, failure_reason=failure_reason)

