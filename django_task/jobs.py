## Moved to "example" app


# from __future__ import print_function
# import time
# import redis
# import logging
# from django.conf import settings
# from .models import CountBeansTask
# from .models import SendEmailTask
# from rq import get_current_job
# from django_rq import job


# @job(CountBeansTask.TASK_QUEUE)
# def count_beans(**kwargs):

#     task = None
#     result = 'SUCCESS'
#     failure_reason = ''

#     try:

#         # this raises a "Could not resolve a Redis connection" exception in sync mode
#         #job = get_current_job()
#         job = get_current_job(connection=redis.Redis.from_url(settings.REDIS_URL))

#         task, created = CountBeansTask.objects.get_or_create(job_id=job.get_id(), **kwargs)
#         task.set_status('STARTED')

#         params = task.retrieve_params_as_dict()
#         num_beans = params['num_beans']

#         for i in range(0, num_beans):
#             time.sleep(0.01)
#             task.set_progress((i + 1) * 100 / num_beans, step=10)
#         #task.set_status('SUCCESS')

#     except Exception as e:
#         if task:
#             task.log(logging.ERROR, str(e))
#         result = 'FAILURE'
#         failure_reason = str(e)

#     finally:
#         if task:
#             task.set_status(result, failure_reason)


# @job(SendEmailTask.TASK_QUEUE)
# def send_email(**kwargs):

#     task = None
#     result = 'SUCCESS'
#     failure_reason = ''

#     try:

#         # this raises a "Could not resolve a Redis connection" exception in sync mode
#         #job = get_current_job()
#         job = get_current_job(connection=redis.Redis.from_url(settings.REDIS_URL))

#         task, created = SendEmailTask.objects.get_or_create(job_id=job.get_id(), **kwargs)
#         task.set_status('STARTED')

#         params = task.retrieve_params_as_dict()

#         recipient_list = params['recipients'].split()
#         sender = params['sender'].strip()
#         subject = params['subject'].strip()
#         message = params['message']

#         from django.core.mail import send_mail
#         send_mail(subject, message, sender, recipient_list)

#         #task.set_status('SUCCESS')

#     except Exception as e:
#         if task:
#             task.log(logging.ERROR, str(e))
#         result = 'FAILURE'
#         failure_reason = str(e)

#     finally:
#         if task:
#             task.set_status(result, failure_reason)

