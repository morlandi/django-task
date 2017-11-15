from django.db import models
from django.conf import settings
from django_task.models import Task


################################################################################

class CountBeansTask(Task):

    num_beans = models.PositiveIntegerField(default=100)

    TASK_QUEUE = settings.QUEUE_DEFAULT
    DEFAULT_VERBOSITY = 2

    # def start_job(self, request):
    #     from .jobs import count_beans
    #     #return count_beans.delay(**self.retrieve_params_as_dict())
    #     return count_beans.delay()

    @staticmethod
    def get_jobfunc():
        from .jobs import count_beans
        return count_beans


class SendEmailTask(Task):

    sender = models.CharField(max_length=256, null=False, blank=False)
    recipients = models.TextField(null=False, blank=False,
        help_text='put addresses in separate rows')
    subject = models.CharField(max_length=256, null=False, blank=False)
    message = models.TextField(null=False, blank=True)

    TASK_QUEUE = settings.QUEUE_LOW
    DEFAULT_VERBOSITY = 2

    # def start_job(self, request):
    #     from .jobs import send_email
    #     #return count_beans.delay(**self.retrieve_params_as_dict())
    #     return send_email.delay()

    @staticmethod
    def get_jobfunc():
        from .jobs import send_email
        return send_email
