from django.core.management.commands.dumpdata import Command as DumpdataCommand
from django.apps import apps
from django_task.models import TaskBase


class Command(DumpdataCommand):

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        # Remove 'args' action
        args_action = [action for action in parser._actions if action.dest=='args'][0]
        parser._remove_action(args_action)

    help = ("Dumps a fixture of all tasks")

    def handle(self, *app_labels, **options):

        # List all Task subclasses
        app_labels = [
        ]
        models = apps.get_models()
        task_models = [model for model in models if issubclass(model, TaskBase)]
        for model in task_models:
            app_labels.append(
                '%s.%s' % (model._meta.app_label, model.__name__)
            )

        super(Command, self).handle(*app_labels, **options)
