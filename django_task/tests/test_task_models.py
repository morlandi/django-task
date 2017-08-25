import json
from django.core.urlresolvers import reverse
from base_testcase import BaseTestCase
from tasks.models import CountBeansTask


class TaskModelTestCase(BaseTestCase):

    def test_count_beans_task_model(self):

        # Excepted param_names: ['num_beans', ]
        param_names = CountBeansTask.retrieve_param_names()
        self.assertListEqual(param_names, ['num_beans', ])

        task = CountBeansTask.objects.create(num_beans=1000)

        # Same as before, but using object instead of class
        param_names = task.retrieve_param_names()
        self.assertListEqual(param_names, ['num_beans', ])

        # Excepted params: {'num_beans': 1000, }
        params = task.retrieve_params_as_dict()
        self.assertDictEqual(params, {'num_beans': 1000, })
