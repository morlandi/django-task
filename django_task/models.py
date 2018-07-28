# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import uuid
import os
import datetime
import time
import logging
import sys
import types
import pprint
import redis
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
import rq
#from rq import get_current_job
#from rq import Worker, Queue
from .utils import format_datetime
from .utils import get_model_from_id
from .app_settings import ALWAYS_EAGER
from .app_settings import LOG_ROOT
from .app_settings import REDIS_URL
from .app_settings import REJECT_IF_NO_WORKER_ACTIVE_FOR_QUEUE


class Task(models.Model):

    class Meta:
        ordering = ('-created_on', )
        get_latest_by = "created_on"
        abstract = True

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self.log_stream = StringIO() if self.LOG_TO_FIELD else None

    # Celery tasks status values:
    # http://docs.celeryproject.org/en/latest/_modules/celery/states.html

    TASK_STATUS_PENDING_VALUES = (
        'PENDING',      #: Task state is unknown (assumed pending since you know the id).
        'RECEIVED',     #: Task was received by a worker (only used in events).
        'STARTED',      #: Task was started by a worker (:setting:`task_track_started`).
        'PROGESS',
    )

    TASK_STATUS_COMPLETED_VALUES = (
        'SUCCESS',      #: Task succeeded
        'FAILURE',      #: Task failed
        'REVOKED',      #: Task was revoked.
        'REJECTED',     #: Task was rejected (only used in events).
        'RETRY',        #: Task is waiting for retry.
        'IGNORED',
        'REJECTED',
    )

    TASK_STATUS_VALUES = TASK_STATUS_PENDING_VALUES + TASK_STATUS_COMPLETED_VALUES

    # TASK_STATUS_VALUES = (
    #     'PENDING',      #: Task state is unknown (assumed pending since you know the id).
    #     'RECEIVED',     #: Task was received by a worker (only used in events).
    #     'STARTED',      #: Task was started by a worker (:setting:`task_track_started`).
    #     'PROGESS',
    #     'SUCCESS',      #: Task succeeded
    #     'FAILURE',      #: Task failed
    #     'REVOKED',      #: Task was revoked.
    #     'REJECTED',     #: Task was rejected (only used in events).
    #     'RETRY',        #: Task is waiting for retry.
    #     'IGNORED',
    #     'REJECTED',
    # )
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
        # return self.get_child()._meta.verbose_name

    @property
    def verbosity(self):
        return self.DEFAULT_VERBOSITY

    @classmethod
    def get_task_from_id(cls, task_id, timeout=1000, retry_count=10):
        """

        """
        return get_model_from_id(cls, task_id, timeout, retry_count)
        # dt = timeout / retry_count
        # for i in range(retry_count):
        #     try:
        #         task = cls.objects.get(id=task_id)
        #         return task
        #     except cls.DoesNotExist:
        #         pass
        #     time.sleep(dt / 1000.0)
        # return None

    # def get_child(self):
    #     """
    #     Return instance of the derived model from base class.

    #     # Adapted from:
    #     #   http://lazypython.blogspot.it/2008/12/playing-with-polymorphism-in-django.html
    #     """

    #     #from django.db.models.fields.reverse_related import OneToOneRel
    #     from django.db.models.fields.related import OneToOneRel
    #     child = self

    #     # Fixes for Django 1.10
    #     # https://docs.djangoproject.com/en/1.9/ref/models/meta/#migrating-from-the-old-api
    #     # Removed in 1.10 many _meta functions as part of the "formalization of the Model._meta api:
    #     # - get_all_field_names
    #     # - get_field_by_name

    #     # for f in self._meta.get_all_field_names():
    #     #     field = self._meta.get_field_by_name(f)[0]
    #     #     ...
    #     for name in [f.name for f in self._meta.get_fields()]:
    #         field = self._meta.get_field(name)
    #         if isinstance(field, OneToOneRel) and field.field.primary_key:
    #             try:
    #                 child = getattr(self, field.get_accessor_name())
    #                 break
    #             except field.model.DoesNotExist:
    #                 pass
    #             # TODO: investigate
    #             # Occasionally receiving RelatedObjectDoesNotExist
    #             except Exception:
    #                 pass
    #     return child

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

        duplicate = self._meta.model.objects.get(id=self.id)
        duplicate.id = uuid.uuid4()
        duplicate.created_on = datetime.datetime.now()
        duplicate.created_by = request.user if request is not None else None
        duplicate.started_on = None
        duplicate.completed_on = None
        duplicate.job_id = ''
        duplicate.status = Task.DEFAULT_TASK_STATUS_VALUE
        duplicate.failure_reason = ''
        duplicate.progress = None

        duplicate.save()

        # Also duplicate related objects
        # Adapted from: https://github.com/team23/django_cloneable/blob/master/django_cloneable/models.py
        dirty = False

        for field in self._meta.many_to_many:
            # handle m2m using through
            if field.remote_field.through and not field.remote_field.through._meta.auto_created:
                print('*** WARNING: m2m using through not supported yet ***')
                # # through-model must be cloneable
                # if hasattr(field.rel.through, 'clone'):
                #     qs = field.rel.through._default_manager.filter(
                #         **{field.m2m_field_name(): self.instance})
                #     for m2m_obj in qs:
                #         m2m_obj.clone(attrs={
                #             field.m2m_field_name(): duplicate
                #         })
                # else:
                #     qs = field.rel.through._default_manager.filter(
                #         **{field.m2m_field_name(): self.instance})
                #     for m2m_obj in qs:
                #         # TODO: Allow switching to different helper?
                #         m2m_clone_helper = ModelCloneHelper(m2m_obj)
                #         m2m_clone_helper.clone(attrs={
                #             field.m2m_field_name(): duplicate
                #         })
            # normal m2m, this is easy
            else:
                objs = getattr(self, field.attname).all()
                #setattr(duplicate, field.attname, objs)
                getattr(duplicate, field.attname).set(objs)
                dirty = True

            if dirty:
                duplicate.save()

        return duplicate

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

        update_fields = ['status', ]
        self.status = status

        if job_id:
            self.job_id = job_id
            update_fields.append('job_id')

        if status in ['STARTED', ]:
            self.started_on = timezone.make_aware(datetime.datetime.now())
            update_fields.append('started_on')
        elif self.check_status_complete():
            self.completed_on = timezone.make_aware(datetime.datetime.now())
            update_fields.append('completed_on')

        if failure_reason is not None:
            # truncate messate to prevent field overflow
            self.failure_reason = failure_reason[:self._meta.get_field('failure_reason').max_length]
            update_fields.append('failure_reason')

        self.log(logging.INFO, '%s [task: "%s", job: "%s"]' % (status, self.id, self.job_id))
        if self.check_status_complete():
            #self.log(logging.INFO, 'params: %s' % str(self.retrieve_params_as_dict()))
            self.log(logging.DEBUG, 'params: \n' + pprint.pformat(self.retrieve_params_as_dict()))

        if commit:
            self.save(update_fields=update_fields)

    def check_status_complete(self):
        return self.status in self.TASK_STATUS_COMPLETED_VALUES
        #return self.status in ['SUCCESS', 'FAILURE', 'REVOKED', 'REJECTED', 'IGNORED', ]

    def status_display(self):
        html = '<div class="task_status" data-task-model="%s.%s" data-task-id="%s" data-task-status="%s" data-task-complete="%d">%s</div>' % (
            self._meta.app_label, self._meta.model_name, str(self.id), self.status, self.check_status_complete(), self.status)
        return mark_safe(html)
    status_display.short_description = _(u'status')
    status_display.admin_order_field = 'status'

    def log_link_display(self):
        html = ''
        info = self._meta.app_label, self._meta.model_name
        if self._logfile() is not None and os.path.exists(self._logfile()):
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

    def check_worker_active_for_queue(self, queue):
        # collect active workers
        workers = rq.Worker.all(connection=redis.Redis.from_url(REDIS_URL))
        # Retrieve active queues;
        # make a flat list out of a list of lists
        active_queue_names = sum([w.queue_names() for w in workers], [])
        return queue.name in active_queue_names

    def run(self, is_async, request=None):

        if self.job_id:
            raise Exception('already scheduled for execution')

        if ALWAYS_EAGER:
            is_async = False

        self.mode = 'ASYNC' if is_async else 'SYNC'
        self.save(update_fields=['mode', ])

        # See: https://github.com/rq/django-rq
        if self.TASK_TIMEOUT > 0:
            queue = django_rq.get_queue(self.TASK_QUEUE, is_async=is_async, default_timeout=self.TASK_TIMEOUT)
        else:
            queue = django_rq.get_queue(self.TASK_QUEUE, is_async=is_async)

        if REJECT_IF_NO_WORKER_ACTIVE_FOR_QUEUE and is_async:
            if not self.check_worker_active_for_queue(queue):
                self.set_status('REJECTED', failure_reason='No active workers for queue', commit=True)
                raise Exception('%s "%s"' % (_('No active workers for queue'), queue.name))

        # Now we accept either a jobfunc or a Job-derived class
        try:
            jobfunc_or_class = self.get_jobfunc()
            if isinstance(jobfunc_or_class, types.FunctionType):
                jobfunc=jobfunc_or_class
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
        # fieldnames = [fname for fname in all_fieldnames
        #     if fname != 'task_ptr' and fname not in base_fieldnames]
        fieldnames = [fname for fname in all_fieldnames if fname not in base_fieldnames]
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
