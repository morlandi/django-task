from django.db import models
from django.conf import settings
from django_task.models import Task


################################################################################

class CountBeansTask(Task):

    num_beans = models.PositiveIntegerField(default=100)

    TASK_QUEUE = settings.QUEUE_DEFAULT
    #TASK_TIMEOUT = 10
    DEFAULT_VERBOSITY = 2
    LOG_TO_FIELD = True

    @staticmethod
    def get_jobfunc():
        from .jobs import CountBeansJob
        return CountBeansJob


class SendEmailTask(Task):

    sender = models.CharField(max_length=256, null=False, blank=False)
    recipients = models.TextField(null=False, blank=False,
        help_text='put addresses in separate rows')
    subject = models.CharField(max_length=256, null=False, blank=False)
    message = models.TextField(null=False, blank=True)

    TASK_QUEUE = settings.QUEUE_LOW
    DEFAULT_VERBOSITY = 2
    LOG_TO_FILE = True

    @staticmethod
    def get_jobfunc():
        from .jobs import SendEmailJob
        return SendEmailJob
