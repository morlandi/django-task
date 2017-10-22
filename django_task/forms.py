# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime
#from suit.widgets import SuitDateWidget, SuitTimeWidget, SuitSplitDateTimeWidget
#from .models import PrintTask


class TaskForm(forms.ModelForm):

    class Meta:
        exclude = [
            'created_on',
            #'created_by',
            'started_on',
            'completed_on',
            'verbosity',
            'job_id',
            'status',
            'failure_reason',
            'progress',
        ]


# class PrintTaskForm(forms.ModelForm):

#     class Meta(TaskForm.Meta):
#         model = PrintTask
#         exclude = TaskForm.Meta.exclude[:] + [
#             'result',
#         ]
#         widgets = {
#             'created_by': forms.HiddenInput(),
#             'societa': forms.HiddenInput(),
#             'registro': forms.HiddenInput(),

#             'data_da': SuitDateWidget,
#             'data_a': SuitDateWidget,
#         }

#     def __init__(self, request, filter_tipo, *args, **kwargs):
#         super(PrintTaskForm, self).__init__(*args, **kwargs)

#         if filter_tipo:

#             visible_fields = PrintTask.list_specific_fields(filter_tipo)
#             if request.user.is_superuser:
#                 visible_fields.append('limite')

#             for name, field in self.fields.items():
#                 if not name in visible_fields:
#                     field.widget = forms.HiddenInput()
