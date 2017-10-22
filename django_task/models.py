# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import uuid
import os
import datetime
import time
import logging
import sys
import django.utils.timezone
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.dispatch import receiver
import django_rq
#from rq import get_current_job
from rq import Worker, Queue
from .utils import format_datetime


class Task(models.Model):

    class Meta:
        ordering = ('-created_on', )
        verbose_name = u"Task"
        verbose_name_plural = u"All Tasks"

    # Celery tasks status values:
    # http://docs.celeryproject.org/en/latest/_modules/celery/states.html
    TASK_STATUS_VALUES = (
        'PENDING',      #: Task state is unknown (assumed pending since you know the id).
        'RECEIVED',     #: Task was received by a worker (only used in events).
        'STARTED',      #: Task was started by a worker (:setting:`task_track_started`).
        'PROGESS',
        'SUCCESS',      #: Task succeeded
        'FAILURE',      #: Task failed
        'REVOKED',      #: Task was revoked.
        'REJECTED',     #: Task was rejected (only used in events).
        'RETRY',        #: Task is waiting for retry.
        'IGNORED',
        'REJECTED',
    )
    DEFAULT_TASK_STATUS_VALUE = TASK_STATUS_VALUES[0]

    TASK_STATUS_CHOICES = ((item, item) for item in TASK_STATUS_VALUES)
    logger = None

    # A base model to save information about an asynchronous task
    id = models.UUIDField('id', default=uuid.uuid4, primary_key=True, unique=True, null=False, blank=False, editable=False)
    created_on = models.DateTimeField(_('created on'), auto_now_add=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='+', on_delete=models.SET_NULL)
    started_on = models.DateTimeField(_('started on'), null=True)
    completed_on = models.DateTimeField(_('completed on'), null=True)
    verbosity = models.IntegerField(_('verbosity'), null=True, blank=True, default=None)
    job_id = models.CharField(_('job id'), max_length=128, null=False, blank=True)
    status = models.CharField(_('status'), max_length=128, null=False, blank=False, db_index=True,
        choices=TASK_STATUS_CHOICES, default=DEFAULT_TASK_STATUS_VALUE)
    failure_reason = models.CharField(_('failure reason'), max_length=256, null=False, blank=True)
    progress = models.IntegerField(_('progress'), null=True, blank=True)

    #
    # To be overridden in derived Task class
    #

    TASK_QUEUE = ''
    DEFAULT_VERBOSITY = 0

    def __str__(self):
        return str(self.id)

    def get_child(self):
        """
        Return instance of the derived model from base class.

        # Adapted from:
        #   http://lazypython.blogspot.it/2008/12/playing-with-polymorphism-in-django.html
        """

        #from django.db.models.fields.reverse_related import OneToOneRel
        from django.db.models.fields.related import OneToOneRel
        child = self

        # Fixes for Django 1.10
        # https://docs.djangoproject.com/en/1.9/ref/models/meta/#migrating-from-the-old-api
        # Removed in 1.10 many _meta functions as part of the "formalization of the Model._meta api:
        # - get_all_field_names
        # - get_field_by_name

        # for f in self._meta.get_all_field_names():
        #     field = self._meta.get_field_by_name(f)[0]
        #     ...
        for name in [f.name for f in self._meta.get_fields()]:
            field = self._meta.get_field(name)
            if isinstance(field, OneToOneRel) and field.field.primary_key:
                try:
                    child = getattr(self, field.get_accessor_name())
                    break
                except field.model.DoesNotExist:
                    pass
        return child

        """
        Retrieve derived class from base class;
        is there a better way ?

        Adapted from:
        https://stackoverflow.com/questions/9771180/model-inheritance-how-can-i-use-overridden-methods#9772220
        """
        # if hasattr(self, 'countbeanstask'):
        #     return self.countbeanstask
        # if hasattr(self, 'sendemailtask'):
        #     return self.sendemailtask
        #raise Exception("Task:get_child() couldn't recognize derived class")
        #return self

    def as_dict(self):
        return {
            'id': str(self.id),
            'created_on': self.created_on.isoformat() if self.created_on else None,
            'created_on_display': format_datetime(self.created_on, include_time=True),
            'created_by': str(self.created_by.id) if self.created_by else None,
            'started_on': self.started_on.isoformat() if self.started_on else None,
            'started_on_display': format_datetime(self.started_on, include_time=True),
            'completed_on': self.completed_on.isoformat() if self.completed_on else None,
            'completed_on_display': format_datetime(self.completed_on, include_time=True),
            'verbosity': self.verbosity,
            'job_id': self.job_id,
            'status': self.status,
            'status_display': self.status_display(),
            'failure_reason': self.failure_reason,
            'progress': self.progress,
            'progress_display': self.progress_display(),
            'completed': self.check_status_complete(),
            'duration': self.duration,
            'duration_display': self.duration_display,
            'extra_fields': {},
        }

    def save(self, *args, **kwargs):
        if self.verbosity is None:
            self.verbosity = self.DEFAULT_VERBOSITY
        super(Task, self).save(*args, **kwargs)

    def clone(self, request=None):
        obj = self._meta.model.objects.get(id=self.id)
        obj.id = uuid.uuid4()
        obj.created_on = datetime.datetime.now()
        obj.created_by = request.user if request is not None else None
        obj.started_on = None
        obj.completed_on = None
        obj.job_id = ''
        obj.status = Task.DEFAULT_TASK_STATUS_VALUE
        obj.failure_reason = ''
        obj.progress = None
        obj.save()
        return obj

    ############################################################################
    # Duration, status and progress management

    @property
    def duration(self):
        dt = None
        try:
            if self.check_status_complete():
                dt = self.completed_on - self.started_on
            else:
                dt = timezone.now() - self.started_on
        except:
            return None
        return int(dt.total_seconds()) if dt is not None else None
    duration.fget.short_description = _('duration')

    @property
    def duration_display(self):
        seconds = self.duration
        if seconds is None:
            return ''
        return time.strftime("%H:%M:%S", time.gmtime(seconds))
    duration_display.fget.short_description = _('duration')

    def set_status(self, status, failure_reason=None, commit=True):

        update_fields = ['status', ]
        self.status = status

        if status in ['STARTED', ]:
            self.started_on = timezone.make_aware(datetime.datetime.now())
            update_fields.append('started_on')
        elif self.check_status_complete():
            self.completed_on = timezone.make_aware(datetime.datetime.now())
            update_fields.append('completed_on')

        if failure_reason is not None:
            self.failure_reason = failure_reason
            update_fields.append('failure_reason')

        #trace('current job: %s (task: %s)' % (job.get_id(), task.id))
        self.log(logging.INFO, '%s [task: "%s", job: "%s"]' % (status, self.id, self.job_id))
        if status in ['STARTED', ]:
            self.log(logging.INFO, 'params: %s' % str(self.retrieve_params_as_dict()))

        if commit:
            self.save(update_fields=update_fields)

    def check_status_complete(self):
        return self.status in ['SUCCESS', 'FAILURE', 'REVOKED', 'REJECTED', 'IGNORED', ]

    def status_display(self):
        html = '<div class="task_status" data-task-id="%s" data-task-status="%s" data-task-complete="%d">%s</div>' % (
            str(self.id), self.status, self.check_status_complete(), self.status)
        return mark_safe(html)
    status_display.short_description = _(u'status')
    status_display.admin_order_field = 'status'

    def set_progress(self, value, step=0, commit=True):
        """
        Update task's progress value;
        If 'step' > 0, the update will occur in chunks.

        To minimize db activity, commit will occur only if progress value has been changed.
        """
        if step > 0:
            progress_step = value / step
            if progress_step != (self.progress and self.progress or 0) / step:
                self.progress = progress_step * step
            else:
                commit = False
        else:
            if value != (self.progress and self.progress or 0):
                self.progress = value
            else:
                commit = False

        if commit:
            self.save(update_fields=['progress', ])

    def get_progress(self):
        return self.progress if self.progress is not None else 0

    def progress_display(self):
        if not self.check_status_complete() or self._meta.model_name== 'task':
            html = str(self.progress) if self.progress is not None else '-'
        else:
            info = self._meta.app_label, self._meta.model_name
            url = reverse('admin:%s_%s_repeat' % info, args=(self.id, ))
            html = '<a href="%s">%s</a>' % (url, _('repeat'))
        return mark_safe(html)
    progress_display.short_description = _('Progress')

    ############################################################################
    # Task logging

    def _logfile(self):
        # Make sure path exists
        if not os.path.exists(settings.TASKLOG_ROOT):
            os.makedirs(settings.TASKLOG_ROOT)
        return os.path.join(settings.TASKLOG_ROOT, str(self.id) + '.log')

    def get_logger(self, verbosity):
        """
        If verbosity <= 0, return None;
        else returns task's own file logger (and creates it if necessary)
        """
        if verbosity >= 1 and self.logger is None:
            # http://stackoverflow.com/questions/29712938/python-celery-how-to-separate-log-files#29733606
            logger_name = 'task_logger_' + str(self.id)
            self.logger = logging.getLogger(logger_name)
            level = logging.DEBUG if verbosity >= 2 else logging.INFO
            self.logger.setLevel(level)

            format_string = '%(asctime)s|%(levelname)s|%(message)s'

            handler = logging.FileHandler(self._logfile(), 'w')
            handler.setFormatter(logging.Formatter(format_string))
            self.logger.addHandler(handler)

            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter('\x1b[1;33;40m%s\x1b[0m' % format_string))
            self.logger.addHandler(handler)

        return self.logger

    def log(self, level, message, *args, **kwargs):
        """
        Log specified message to task's own file logger
        """
        logger = self.get_logger(self.verbosity)
        if logger:
            logger.log(level, message, *args, **kwargs)

    ############################################################################
    # Job execution

    def start_job(self, request):
        """
        To be overridden calling the specific job
        """
        pass

    def check_worker_active_for_queue(self):

        #
        # TODO: copied from sample project; verify
        #

        redis_connection = django_rq.get_connection(self.TASK_QUEUE)
        # ???
        #if len([x for x in Worker.all(connection=redis_conn) if settings.DJANGO_TEST_RQ_LOW_QUEUE in x.queue_names()]) == 0:
        #     messages.add_message(self.request, messages.ERROR, )
        workers = [worker for worker in Worker.all(connection=redis_connection) if self.TASK_QUEUE in worker.queue_names()]
        if len(workers) <= 0:
            raise Exception('%s "%s"' % (_('No active workers for queue'), self.TASK_QUEUE))

    def run(self, request, async):

        if self.job_id:
            raise Exception('already scheduled for execution')

        #self.check_worker_active_for_queue() !!!

        job = None
        if async:
            job = self.start_job(request)
        else:
            raise Exception('TODO: sync call')

        self.job_id = job.id if job else None
        self.save(update_fields=['job_id'])
        return job

    @classmethod
    def retrieve_param_names(cls):
        """
        List specific parameters of derived task
        """
        base_fieldnames = [f.name for f in Task._meta.get_fields()]
        all_fieldnames = [f.name for f in cls._meta.get_fields()]
        fieldnames = [fname for fname in all_fieldnames
            if fname != 'task_ptr' and fname not in base_fieldnames]
        return fieldnames

    def retrieve_params_as_dict(self):
        keys = self.retrieve_param_names()
        return dict([(key, getattr(self, key)) for key in keys])

    def retrieve_params_as_table(self):
        params = self.retrieve_params_as_dict()
        html = '<table>' + \
            '\n'.join(['<tr><td>%s</td><td>%s</td></tr>' % (key, value) for key, value in params.items()]) + \
            '</table>'
        return mark_safe(html)


@receiver(models.signals.post_delete, sender=Task)
def on_task_delete_cleanup(sender, instance, **kwargs):
    """
    Autodelete logfile on Task delete
    """
    logfile = instance._logfile()
    if os.path.isfile(logfile):
        os.remove(logfile)


# ################################################################################
#  Moved to "example" app
#
# class CountBeansTask(Task):
#
#     num_beans = models.PositiveIntegerField(default=100)
#
#     TASK_QUEUE = settings.QUEUE_DEFAULT
#     DEFAULT_VERBOSITY = 2
#
#     def start_job(self, request):
#         from .jobs import count_beans
#         #return count_beans.delay(**self.retrieve_params_as_dict())
#         return count_beans.delay()
#
#
# class SendEmailTask(Task):
#
#     sender = models.CharField(max_length=256, null=False, blank=False)
#     recipients = models.TextField(null=False, blank=False,
#         help_text='put addresses in separate rows')
#     subject = models.CharField(max_length=256, null=False, blank=False)
#     message = models.TextField(null=False, blank=True)
#
#     TASK_QUEUE = settings.QUEUE_LOW
#     DEFAULT_VERBOSITY = 2
#
#     def start_job(self, request):
#         from .jobs import send_email
#         #return count_beans.delay(**self.retrieve_params_as_dict())
#         return send_email.delay()
