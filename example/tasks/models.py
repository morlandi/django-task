from django.db import models
from django.conf import settings
from django_task.models import TaskRQ
from django_task.models import TaskThreaded


################################################################################

class CountBeansTask(TaskRQ):

    num_beans = models.PositiveIntegerField(default=100)
    task_verbosity = models.PositiveIntegerField(null=False, blank=False, default=2,
        choices=((0,'0'), (1,'1'), (2,'2'), (3,'3')),
    )

    TASK_QUEUE = settings.QUEUE_DEFAULT
    #TASK_TIMEOUT = 10
    DEFAULT_VERBOSITY = 2
    LOG_TO_FIELD = True
    LOG_TO_FILE = False

    @staticmethod
    def get_jobclass():
        from .jobs import CountBeansJob
        return CountBeansJob


class CountBeansTaskThreaded(TaskThreaded):

    num_beans = models.PositiveIntegerField(default=100)

    TASK_QUEUE = None
    #TASK_TIMEOUT = 10
    DEFAULT_VERBOSITY = 2
    LOG_TO_FIELD = True
    LOG_TO_FILE = False

    @staticmethod
    def get_jobclass():
        from .jobs import CountBeansJob
        return CountBeansJob


class SendEmailTask(TaskRQ):

    sender = models.CharField(max_length=256, null=False, blank=False)
    recipients = models.TextField(null=False, blank=False,
        help_text='put addresses in separate rows')
    subject = models.CharField(max_length=256, null=False, blank=False)
    message = models.TextField(null=False, blank=True)

    TASK_QUEUE = settings.QUEUE_LOW
    #TASK_TIMEOUT = 10
    DEFAULT_VERBOSITY = 2
    LOG_TO_FIELD = True
    LOG_TO_FILE = False

    @staticmethod
    def get_jobclass():
        from .jobs import SendEmailJob
        return SendEmailJob
