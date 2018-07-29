import time
import django
import sys
from django_task.tests.models import CountBeansTask


class CountBeansTestCase(django.test.TransactionTestCase):

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

    def test_count_beans_task_run(self):

        task = CountBeansTask.objects.create(num_beans=100)
        print('task.id: %s' % str(task.id))
        job = task.run(is_async=False)
        print('job.id: %s' % job.id)

        # print('Waiting for task completed:')
        # while True:
        #     task = CountBeansTask.objects.get(id=task.id)
        #     if task.check_status_complete():
        #         break
        #     print('task status: %s' % task.status)
        #     sys.stdout.write('.')
        #     sys.stdout.flush()
        #     time.sleep(1.0)

        task = CountBeansTask.objects.get(id=task.id)
        self.assertTrue(task.check_status_complete())
