import time
import django
import sys
import mock
from django.contrib.auth import get_user_model
try:
    from django.urls import reverse
except:
    from django.core.urlresolvers import reverse
from .base_case import AdminCase
from tasks.models import CountBeansTask


class CountBeansTestCase(AdminCase):

    def setUp(self):
        User = get_user_model()

        self.admin_username = 'admin'
        self.admin_password = 'admin_password'
        self.admin = User.objects.create_superuser(
            self.admin_username,
            self.admin_username+'@noreply.com',
            self.admin_password
        )

        self.guest_username = 'guest'
        self.guest_password = 'guest_password'
        self.guest = User.objects.create_user(
            self.guest_username,
            '%s@djest.generated' % self.guest_username,
            self.guest_password,
            is_staff=True
        )
        #self.set_user_permissions(self.guest)

        super(CountBeansTestCase, self).setUp()
        #self.populate()

    def dot(self):
        #print('.', end='')
        sys.stdout.write('.')
        sys.stdout.flush()

    def wait_task_completion(self, task_id):
        print('Waiting for task completed:')
        while True:
            task = CountBeansTask.objects.get(id=task_id)
            if task.check_status_complete():
                break
            self.dot()
            time.sleep(0.1)
        #print(task.result.file.readline())

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

        task = CountBeansTask.objects.create(num_beans=10)
        print('task.id: %s' % str(task.id))
        job = task.run(is_async=True)
        print('job.id: %s' % job.id)

        self.assertFalse(task.async_mode)
        # if task.async_mode:
        #     print('Waiting for task completed:')
        #     while True:
        #         task = CountBeansTask.objects.get(id=task.id)
        #         if task.check_status_complete():
        #             break
        #         #print('task status: %s' % task.status)
        #         sys.stdout.write('.')
        #         sys.stdout.flush()
        #         time.sleep(1.0)

        task = CountBeansTask.objects.get(id=task.id)
        self.assertTrue(task.check_status_complete())

    def test_count_beans_task_run_via_admin(self):

        self.login(self.admin, self.admin_password)
        self.assertTrue(self.response)

        # go to the changelist page
        self.get(reverse('admin:tasks_countbeanstask_changelist'))

        # count the no. of models on the page
        self.assert_result_count(0)

        # add another one through the admin
        self.post(
            reverse('admin:tasks_countbeanstask_add'),
            {
                'num_beans': 10,
            }
        )

        # count the no. of models on the page
        self.assert_result_count(1)

        # Check new task
        task = CountBeansTask.objects.latest()
        self.wait_task_completion(task.id)
        self.assertTrue(task.check_status_complete())
