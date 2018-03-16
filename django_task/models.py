# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import uuid
import os
import datetime
import time
import logging
import sys
import types
try:
    from cStringIO import StringIO      # Python 2
except ImportError:
    from io import StringIO
import django.utils.timezone
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from django.utils import timezone
try:
    from django.urls import reverse
except:
    from django.core.urlresolvers import reverse
from django.dispatch import receiver
import django_rq
#from rq import get_current_job
#from rq import Worker, Queue
from .utils import format_datetime
from .app_settings import ALWAYS_EAGER
from .app_settings import LOG_ROOT


class Task(models.Model):

    class Meta:
        ordering = ('-created_on', )
        verbose_name = u"Task"
        verbose_name_plural = u"All Tasks"
        get_latest_by = "created_on"

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self.log_stream = StringIO() if self.LOG_TO_FIELD else None

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

    TASK_MODE_VALUES = (
        'UNKNOWN',
        'SYNC',
        'ASYNC',
    )
    DEFAULT_TASK_MODE_VALUE = TASK_MODE_VALUES[0]
    TASK_MODE_CHOICES = ((item, item) for item in TASK_MODE_VALUES)

    logger = None
    log_stream = None

    # A base model to save information about an asynchronous task
    id = models.UUIDField('id', default=uuid.uuid4, primary_key=True, unique=True, null=False, blank=False, editable=False)
    description = models.CharField(_('description'), max_length=256, null=False, blank=True)
    created_on = models.DateTimeField(_('created on'), auto_now_add=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='+', on_delete=models.SET_NULL)
    started_on = models.DateTimeField(_('started on'), null=True)
    completed_on = models.DateTimeField(_('completed on'), null=True)
    verbosity = models.IntegerField(_('verbosity'), null=True, blank=True, default=None)
    job_id = models.CharField(_('job id'), max_length=128, null=False, blank=True)
    status = models.CharField(_('status'), max_length=128, null=False, blank=False, db_index=True,
        choices=TASK_STATUS_CHOICES, default=DEFAULT_TASK_STATUS_VALUE)
    mode = models.CharField(_('mode'), max_length=128, null=False, blank=False, db_index=True,
        choices=TASK_MODE_CHOICES, default=DEFAULT_TASK_MODE_VALUE)
    failure_reason = models.CharField(_('failure reason'), max_length=256, null=False, blank=True)
    progress = models.IntegerField(_('progress'), null=True, blank=True)
    log_text = models.TextField(_('log text'), null=False, blank=True)

    #
    # To be overridden in derived Task class
    #

    TASK_QUEUE = ''
    TASK_TIMEOUT = 0
    DEFAULT_VERBOSITY = 0
    LOG_TO_FILE = False
    LOG_TO_FIELD = False

    def __str__(self):
        if self.description:
            return self.description
        return str(self.id)

    @classmethod
    def get_task_from_id(cls, task_id, timeout=1000, retry_count=10):
        """

        """
        dt = timeout / retry_count
        for i in range(retry_count):
            try:
                task = cls.objects.get(id=task_id)
                return task
            except cls.DoesNotExist:
                pass
            time.sleep(dt / 1000.0)
        return None

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
                # TODO: investigate
                # Occasionally receiving RelatedObjectDoesNotExist
                except Exception:
                    pass
        return child

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
            'log_link_display': self.log_link_display(),
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

        if self.LOG_TO_FIELD:
            text = self.log_stream.getvalue()
            if len(text):
                # Update 'log_text' field and make sure it'll be saved
                self.log_text = text
                if 'update_fields' in kwargs:
                    if 'log_text' not in kwargs['update_fields']:
                        kwargs['update_fields'].append('log_text')

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
    def async_mode(self):
        return self.mode == 'ASYNC'

    @property
    def sync_mode(self):
        return self.mode == 'SYNC'

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

    def set_status(self, status, job_id=None, failure_reason=None, commit=True):

        self.status = status

        if job_id:
            self.job_id = job_id

        if status in ['STARTED', ]:
            self.started_on = timezone.make_aware(datetime.datetime.now())
        elif self.check_status_complete():
            self.completed_on = timezone.make_aware(datetime.datetime.now())

        if failure_reason is not None:
            # truncate messate to prevent field overflow
            self.failure_reason = failure_reason[:self._meta.get_field('failure_reason').max_length]

        self.log(logging.INFO, '%s [task: "%s", job: "%s"]' % (status, self.id, self.job_id))
        if self.check_status_complete():
            self.log(logging.INFO, 'params: %s' % str(self.retrieve_params_as_dict()))

        if commit:
            self.save()

    def check_status_complete(self):
        return self.status in ['SUCCESS', 'FAILURE', 'REVOKED', 'REJECTED', 'IGNORED', ]

    def status_display(self):
        html = '<div class="task_status" data-task-id="%s" data-task-status="%s" data-task-complete="%d">%s</div>' % (
            str(self.id), self.status, self.check_status_complete(), self.status)
        return mark_safe(html)
    status_display.short_description = _(u'status')
    status_display.admin_order_field = 'status'

    def log_link_display(self):
        html = ''
        info = self._meta.app_label, self._meta.model_name
        if os.path.exists(self._logfile()):
            url = reverse('admin:%s_%s_viewlogfile' % info, args=(self.id, ))
            html += '<a href="%s">%s</a>' % (url, "Download ")
        if self.log_text:
            url = reverse('admin:%s_%s_viewlogtext' % info, args=(self.id, ))
            html += '<a class="logtext" href="%s">%s</a>' % (url, "QuickView ")
            html += '<a href="%s">%s</a>' % (url, "View ")
        return mark_safe(html)
    log_link_display.short_description = _(u'log')

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
        if LOG_ROOT:
            if not os.path.exists(LOG_ROOT):
                os.makedirs(LOG_ROOT)
            return os.path.join(LOG_ROOT, str(self.id) + '.log')
        return None

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

            # Log to file
            if self.LOG_TO_FILE:
                logfile = self._logfile()
                if logfile:
                    handler = logging.FileHandler(logfile, 'w')
                    handler.setFormatter(logging.Formatter(format_string))
                    self.logger.addHandler(handler)

            # Log to stdout
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter('\x1b[1;33;40m%s\x1b[0m' % format_string))
            self.logger.addHandler(handler)

            # Log to text field
            if self.LOG_TO_FIELD:
                handler = logging.StreamHandler(self.log_stream)
                handler.setFormatter(logging.Formatter(format_string))
                self.logger.addHandler(handler)

        return self.logger

    def log(self, level, message, *args, **kwargs):
        """
        Log specified message to task's own file logger
        """

        logger = self.get_logger(self.verbosity)
        if logger:
            logger.log(level, message, *args, **kwargs)
            # if self.LOG_TO_FIELD:
            #     self.log_text = self.log_text + message + '\n'

    ############################################################################
    # Job execution

    # def start_job(self, request):
    #     """
    #     To be overridden calling the specific job
    #     """
    #     pass

    @staticmethod
    def get_jobfunc():
        """
        To be overridden supplying a specific job func.
        TODO: use job registry instead ?
        """
        pass

    # def check_worker_active_for_queue(self):

    #     #
    #     # TODO: copied from sample project; verify
    #     #

    #     redis_connection = django_rq.get_connection(self.TASK_QUEUE)
    #     # ???
    #     #if len([x for x in Worker.all(connection=redis_conn) if settings.DJANGO_TEST_RQ_LOW_QUEUE in x.queue_names()]) == 0:
    #     #     messages.add_message(self.request, messages.ERROR, )
    #     workers = [worker for worker in Worker.all(connection=redis_connection) if self.TASK_QUEUE in worker.queue_names()]
    #     if len(workers) <= 0:
    #         raise Exception('%s "%s"' % (_('No active workers for queue'), self.TASK_QUEUE))

    def run(self, async, request=None):

        if self.job_id:
            raise Exception('already scheduled for execution')

        #self.check_worker_active_for_queue() !!!

        # This has been refactored in v1.3.0
        #
        # job = None
        # jobfunc = self.get_jobfunc()
        # if ALWAYS_EAGER or not async:
        #     queue = django_rq.get_queue(self.TASK_QUEUE, async=False)
        #     job = queue.enqueue(jobfunc, self.id)
        # else:
        #     job = jobfunc.delay(self.id)

        if ALWAYS_EAGER:
            async = False

        self.mode = 'ASYNC' if async else 'SYNC'
        self.save(update_fields=['mode', ])

        # See: https://github.com/rq/django-rq
        if self.TASK_TIMEOUT > 0:
            queue = django_rq.get_queue(self.TASK_QUEUE, async=async, default_timeout=self.TASK_TIMEOUT)
        else:
            queue = django_rq.get_queue(self.TASK_QUEUE, async=async)

        # Now we accept either a jobfunc or a Job-derived class
        try:
            jobfunc_or_class = self.get_jobfunc()
            if isinstance(jobfunc_or_class, types.FunctionType):
                jobfunc = jobfunc_or_class
                job = queue.enqueue(jobfunc, self.id)
            else:
                jobclass = jobfunc_or_class
                #assert isinstance(jobclass, Job):
                job = queue.enqueue(jobclass.run, task_class=self.__class__, task_id=self.id)
        except:
            raise Exception('Provide either a function or a class derived from Job')

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
