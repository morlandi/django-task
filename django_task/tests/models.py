from django.db import models
from django.conf import settings
from django_task.models import TaskRQ


################################################################################

class CountBeansTask(TaskRQ):

    num_beans = models.PositiveIntegerField(default=100)

    TASK_QUEUE = settings.QUEUE_DEFAULT
    #TASK_TIMEOUT = 10
    DEFAULT_VERBOSITY = 2
    LOG_TO_FIELD = True

    @staticmethod
    def get_jobclass():
        from .jobs import CountBeansJob
        return CountBeansJob

