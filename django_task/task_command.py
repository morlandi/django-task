import distutils
import sys
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from .models import TaskThreaded


class TaskCommand(BaseCommand):
    """
    Base class for task-related management commands
    """
    help = 'Run task asynchronously; used to schedule tasks via crontab'

    def add_arguments(self, parser):
        parser.add_argument('--queue', '-Q', default='', help='The queue to work on')
        parser.add_argument('--sync', action="store_true", default=False, help='Run task synchronously')

    def run_task(self, TaskClass, created_by=None, **options):
        task = None
        try:
            param_names = TaskClass.retrieve_param_names()

            # If verbosity has been explicitly supplied on the command line,
            # use it to set task verbosity;
            # otherwise, keep the default value suggested by the task Model
            if 'task_verbosity' in param_names:
                if ('-v' in sys.argv or '--verbosity' in sys.argv) and 'verbosity' in options:
                    options['task_verbosity'] = options['verbosity']

            params = dict([item for item in options.items() if item[0] in param_names])

            if created_by is not None:
                params.update({'created_by': created_by})

            task = TaskClass.objects.create(**params)

            is_async = not options.get('sync')
            if issubclass(TaskClass, TaskThreaded):
                task.run(is_async=is_async, daemon=False)
            else:
                task.run(is_async=is_async)
        except Exception as e:
            raise CommandError('[%s] ERROR: %s' % (timezone.now().isoformat(), str(e)))

        self.stdout.write('[%s] %s scheduled (task=%s)' % (timezone.now().isoformat(), TaskClass.__name__, str(task.id)))
        return task.id if task is not None else None

