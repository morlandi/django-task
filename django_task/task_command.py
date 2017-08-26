from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import django_rq


class TaskCommand(BaseCommand):
    """
    Base class for task-related management commands
    """


    help = 'Run task asynchronously; used to schedule tasks via crontab'

    def add_arguments(self, parser):
        parser.add_argument('--queue', '-Q', default='', help='The queue to work on')
        #parser.add_argument('num_beans', type=int)

    # def handle(self, *args, **options):
    #     try:
    #         #num_beans = int(options['num_beans'])
    #         queue_name = options['queue']

    #         from tasks.jobs import count_beans
    #         from tasks.models import CountBeansTask as MyTask

    #         param_names = MyTask.retrieve_param_names()
    #         params = dict([item for item in options.items() if item[0] in param_names])

    #         if queue_name:
    #             queue = django_rq.get_queue(queue_name)
    #             #queue.enqueue(count_beans, num_beans=num_beans)
    #             queue.enqueue(count_beans, **params)
    #         else:
    #             #count_beans.delay(num_beans=num_beans)
    #             count_beans.delay(**params)

    #     except Exception as e:
    #         raise CommandError('ERROR: %s' % str(e))
    #     self.stdout.write('Done')

    def run_task(self, TaskClass, job_func, **options):
        try:
            queue_name = options['queue']

            param_names = TaskClass.retrieve_param_names()
            params = dict([item for item in options.items() if item[0] in param_names])

            if queue_name:
                queue = django_rq.get_queue(queue_name)
                #queue.enqueue(count_beans, num_beans=num_beans)
                job = queue.enqueue(job_func, **params)
            else:
                #count_beans.delay(num_beans=num_beans)
                job = job_func.delay(**params)

        except Exception as e:
            raise CommandError('[%s] ERROR: %s' % (timezone.now().isoformat(), str(e)))

        self.stdout.write('[%s] %s scheduled (job=%s)' % (timezone.now().isoformat(), TaskClass.__name__, job.get_id()))
