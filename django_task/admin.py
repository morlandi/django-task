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
try:
    from django.urls import reverse
except:
    from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from .models import Task
#from .models import CountBeansTask
#from .models import SendEmailTask
from .utils import get_object_by_uuid_or_404
from .utils import format_datetime


#@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    class Media:
        css = {
            'all': ('css/django_task.css',)
        }
        js = (
            "js/django_task.js",
        )

    def get_queryset(self, request):
        """
        Superuser can view all tasks, while other users have access to their own tasks only
        """
        qs = super(TaskAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

    list_display = ['__str__', 'created_on_display', 'created_by', 'started_on_display', 'completed_on_display',
        'duration_display', 'status_display', 'progress_display', 'mode']
    list_filter = ['created_on', 'started_on', 'status', ]
    date_hierarchy = 'created_on'

    readonly_fields = ['description', 'created_on', 'created_by', 'started_on', 'completed_on', 'job_id',
        'status', 'failure_reason', 'progress', 'verbosity', 'mode', 'log_text', ]

    def get_list_display(self, request):
        list_display = self.list_display[:]
        # Superuser has access to task's log
        if request.user.is_superuser:
            list_display.append('log_link_display')
        # if self.model._meta.model_name == 'task':
        #     list_display.append('model_name_display')
        return list_display

    def get_fieldsets(self, request, obj=None):
        fields = super(TaskAdmin, self).get_fieldsets(request, obj)[0][1]['fields']
        base_fieldnames = [f.name for f in Task._meta.get_fields()]
        primary_fields = [f for f in fields if f not in base_fieldnames]
        secondary_fields = [f for f in fields if f not in primary_fields]
        fieldsets = [
            (None, {'fields': primary_fields}),
        ]

        if obj is not None:
            fieldsets.append(
                (_('Task Details'), {'fields': secondary_fields})
            )

        return fieldsets

    search_fields = ['=id', '=job_id', ]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(TaskAdmin, self).get_readonly_fields(request, obj)
        if obj:
            # Do not modify already existing tasks
            return readonly_fields + obj.retrieve_param_names()
        return readonly_fields

    def get_prepopulated_fields(self, request, obj=None):
        """
        Hack: when editing an existing object, all fields have been set as readonly;
        so we need to clear prepopulate_fields dict to avoid a runtime error.

        "prepopulated_fields crashes with get_readonly_fields",
        see: https://code.djangoproject.com/ticket/13618
        """
        if obj:
            return {}
        prepopulated_fields = super(TaskAdmin, self).get_prepopulated_fields(request, obj)
        return prepopulated_fields

    # def model_name_display(self, obj):
    #     try:
    #         model_name = obj.get_child()._meta.model_name
    #     except:
    #         model_name = self.model._meta.model_name
    #     return model_name
    # model_name_display.short_description = _('Task')

    def created_on_display(self, obj):
        return format_datetime(obj.created_on, include_time=True)
    created_on_display.short_description = _('Created on')
    created_on_display.admin_order_field = 'created_on'

    def completed_on_display(self, obj):
        return format_datetime(obj.completed_on, include_time=True)
    completed_on_display.short_description = _('Completed on')
    completed_on_display.admin_order_field = 'completed_on'

    def started_on_display(self, obj):
        if obj.job_id:
            html = format_datetime(obj.started_on, include_time=True)
        else:
            info = self.model._meta.app_label, self.model._meta.model_name
            url = reverse('admin:%s_%s_run' % info, args=(obj.id, ))
            html = '<a href="%s">%s</a>' % (url, _('run'))
        return mark_safe(html)
    started_on_display.short_description = _('Started on')
    started_on_display.admin_order_field = 'started_on'

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
            url(r'^(?P<object_id>[^/]+)/view-logfile/$',
                self.admin_site.admin_view(self.view_logfile), {},
                name="%s_%s_viewlogfile" % info),
            url(r'^(?P<object_id>[^/]+)/view-logtext/$',
                self.admin_site.admin_view(self.view_logtext), {},
                name="%s_%s_viewlogtext" % info),
        ]
        return my_urls + urls

    def run(self, object_id, request):
        try:
            obj = get_object_by_uuid_or_404(self.model, object_id)
            job = obj.run(is_async=True, request=request)
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
            job = clone.run(is_async=True, request=request)
            messages.info(request, _('Task "%s" scheduled for execution (job: "%s")') % (clone.id, job.get_id()))
        except Exception as e:
            messages.error(request, str(e))
            if settings.DEBUG:
                messages.warning(request, mark_safe('<br />'.join(traceback.format_exc().split('\n'))))
        info = self.model._meta.app_label, self.model._meta.model_name
        return HttpResponseRedirect(reverse("admin:%s_%s_changelist" % info))

    def view_logfile(self, request, object_id):
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

    def view_logtext(self, request, object_id):
        obj = get_object_by_uuid_or_404(self.model, object_id)
        response = HttpResponse(obj.log_text, content_type='text/plain; charset=utf-8')
        return response

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super(TaskAdmin, self).save_model(request, obj, form, change)
        # v1.2.3: we postpone autorun to response_add() to have M2M task parameters (if any) ready
        # if not change:
        #     self.run(str(obj.id), request)

    def response_add(self, request, obj, post_url_continue=None):
        response = super().response_add(request, obj, post_url_continue)
        self.run(str(obj.id), request)
        return response

    def has_add_permission(self, request):
        if self.model._meta.model_name == 'task':
            return False
        return super(TaskAdmin, self).has_add_permission(request)
