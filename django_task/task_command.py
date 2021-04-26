import distutils
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
        try:
            param_names = TaskClass.retrieve_param_names()
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

