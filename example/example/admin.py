from django.contrib import admin
from django_task.admin import TaskAdmin

from .models import CountBeansTask
from .models import SendEmailTask


@admin.register(CountBeansTask)
class CountBeansTaskAdmin(TaskAdmin):

    def get_list_display(self, request):
        list_display = super(CountBeansTaskAdmin, self).get_list_display(request)
        return list_display + ['num_beans', ]


@admin.register(SendEmailTask)
class SendEmailTaskAdmin(TaskAdmin):

    pass
