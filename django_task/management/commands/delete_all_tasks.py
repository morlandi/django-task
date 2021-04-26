from django.core.management.base import BaseCommand
from django.apps import apps
from django_task.models import TaskBase
from django_task.app_settings import LOG_ROOT


class Command(BaseCommand):

    help = ("Delete all tasks from db tables")

    def handle(self, *app_labels, **options):

        # Delete all subtasks, then Tak itself
        models = apps.get_models()
        task_models = [model for model in models if issubclass(model, TaskBase)]
        for model in task_models:
            print('Deleting %s objects (%d) ...' % (model.__name__, model.objects.count()))
            model.objects.all().delete()
        print('Done.')
        print('Dont\' forget to remove log files from folder "%s"' % LOG_ROOT)
