from __future__ import unicode_literals
import traceback
import os
import mimetypes
from wsgiref.util import FileWrapper
from django.http import StreamingHttpResponse
from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from .models import Task
#from .models import CountBeansTask
#from .models import SendEmailTask
from .utils import get_object_by_uuid_or_404
from .utils import format_datetime


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    class Media:
        css = {
            'all': ('css/django_task.css',)
        }
        js = (
            "js/django_task.js",
        )

    list_display = ['created_on_display', 'created_by', 'started_on_display', 'completed_on_display',
        'duration_display', 'status_display', 'progress_display', 'log_link', ]
    list_filter = ['created_on', 'started_on', 'status', ]
    date_hierarchy = 'created_on'

    readonly_fields = ['created_on', 'created_by', 'started_on', 'completed_on', 'job_id',
        'status', 'failure_reason', 'progress', 'verbosity', ]

    def get_list_display(self, request):
        if self.model._meta.model_name == 'task':
            return self.list_display + ['model_name_display', ]
        return self.list_display

    def get_fieldsets(self, request, obj=None):
        fields = super(TaskAdmin, self).get_fieldsets(request, obj)[0][1]['fields']
        base_fieldnames = [f.name for f in Task._meta.get_fields()]
        primary_fields = [f for f in fields if f not in base_fieldnames]
        secondary_fields = [f for f in fields if f not in primary_fields]
        fieldsets = [
            (None, {'fields': primary_fields}),
            (_('Task Details'), {'fields': secondary_fields})
        ]
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(TaskAdmin, self).get_readonly_fields(request, obj)
        if obj:
            # Do not modify already existing tasks
            return readonly_fields + obj.retrieve_param_names()
        return readonly_fields

    def model_name_display(self, obj):
        try:
            model_name = obj.get_child()._meta.model_name
        except:
            model_name = self.model._meta.model_name
        return model_name
    model_name_display.short_description = _('Task')

    def created_on_display(self, obj):
        return format_datetime(obj.created_on, include_time=True)
    created_on_display.short_description = _('Created on')

    def completed_on_display(self, obj):
        return format_datetime(obj.completed_on, include_time=True)
    completed_on_display.short_description = _('Completed on')

    def log_link(self, obj):
        html = ''
        if os.path.exists(obj._logfile()):
            info = self.model._meta.app_label, self.model._meta.model_name
            url = reverse('admin:%s_%s_viewlog' % info, args=(obj.id, ))
            html = '<a href="%s">%s</a>' % (url, "log")
        return mark_safe(html)
    log_link.short_description = _('Log')

    def started_on_display(self, obj):
        if obj.job_id:
            html = format_datetime(obj.started_on, include_time=True)
        else:
            info = self.model._meta.app_label, self.model._meta.model_name
            url = reverse('admin:%s_%s_run' % info, args=(obj.id, ))
            html = '<a href="%s">%s</a>' % (url, _('run'))
        return mark_safe(html)
    started_on_display.short_description = _('Started on')

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super(TaskAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<object_id>[^/]+)/run/$',
                self.admin_site.admin_view(self.run), {},
                name="%s_%s_run" % info),
            url(r'^(?P<object_id>[^/]+)/repeat/$',
                self.admin_site.admin_view(self.repeat), {},
                name="%s_%s_repeat" % info),
            url(r'^(?P<object_id>[^/]+)/view-log/$',
                self.admin_site.admin_view(self.view_log), {},
                name="%s_%s_viewlog" % info),
        ]
        return my_urls + urls

    def run(self, request, object_id):
        try:
            obj = get_object_by_uuid_or_404(self.model, object_id)
            job = obj.run(request, async=True)
            messages.info(request, _('Task "%s" scheduled for execution (job: "%s")') % (object_id, job.get_id()))
        except Exception as e:
            messages.error(request, str(e))
            if settings.DEBUG:
                messages.warning(request, mark_safe('<br />'.join(traceback.format_exc().split('\n'))))
        info = self.model._meta.app_label, self.model._meta.model_name
        return HttpResponseRedirect(reverse("admin:%s_%s_changelist" % info))

    def repeat(self, request, object_id):
        try:
            source_obj = get_object_by_uuid_or_404(self.model, object_id)
            clone = source_obj.clone(request)
            #messages.info(request, _('Task "%s" cloned to "%s"') % (source_obj.id, clone.id))
            job = clone.run(request, async=True)
            messages.info(request, _('Task "%s" scheduled for execution (job: "%s")') % (clone.id, job.get_id()))
        except Exception as e:
            messages.error(request, str(e))
            if settings.DEBUG:
                messages.warning(request, mark_safe('<br />'.join(traceback.format_exc().split('\n'))))
        info = self.model._meta.app_label, self.model._meta.model_name
        return HttpResponseRedirect(reverse("admin:%s_%s_changelist" % info))

    def view_log(self, request, object_id):
        # NOTE:
        # starting from Django 1.10, a specific FileResponse will be avaibale:
        #     https://docs.djangoproject.com/en/1.10/ref/request-response/#fileresponse-objects
        obj = get_object_by_uuid_or_404(self.model, object_id)
        filename = obj._logfile()

        # wrapper = FileWrapper(open(filename, 'r'))
        # response = HttpResponse(wrapper, content_type='text/plain')

        # Here is another approach, which will stream your file in chunks without loading it in memory.
        # https://stackoverflow.com/questions/8600843/serving-large-files-with-high-loads-in-django#8601118
        chunk_size = 8192
        response = StreamingHttpResponse(
            FileWrapper(open(filename, 'rb'), chunk_size),
            content_type=mimetypes.guess_type(filename)[0])

        response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
        response['Content-Length'] = os.path.getsize(filename)
        return response

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super(TaskAdmin, self).save_model(request, obj, form, change)
        self.run(request, str(obj.id))

    def has_add_permission(self, request):
        if self.model._meta.model_name == 'task':
            return False
        return super(TaskAdmin, self).has_add_permission(request)


################################################################################
#  Moved to "example" app
#
# @admin.register(CountBeansTask)
# class CountBeansTaskAdmin(TaskAdmin):
#
#     def get_list_display(self, request):
#         list_display = super(CountBeansTaskAdmin, self).get_list_display(request)
#         return list_display + ['num_beans', ]
#
#
# @admin.register(SendEmailTask)
# class SendEmailTaskAdmin(TaskAdmin):
#
#     pass
#
