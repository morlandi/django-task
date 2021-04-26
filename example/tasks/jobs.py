import time
import logging
import traceback
from django.conf import settings
from .models import CountBeansTask
from .models import SendEmailTask
from django_task.job import Job


class CountBeansJob(Job):

    @staticmethod
    def execute(job, task):
        num_beans = task.num_beans
        for i in range(0, num_beans):
            time.sleep(0.01)
            task.set_progress((i + 1) * 100 / num_beans, step=10)


class SendEmailJob(Job):

    @staticmethod
    def execute(job, task):
        recipient_list = task.recipients.split()
        sender = task.sender.strip()
        subject = task.subject.strip()
        message = task.message

        from django.core.mail import send_mail
        send_mail(subject, message, sender, recipient_list)
