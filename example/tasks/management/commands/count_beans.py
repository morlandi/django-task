from django_task.task_command import TaskCommand


class Command(TaskCommand):

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('num_beans', type=int)

    def handle(self, *args, **options):
        from tasks.models import CountBeansTask
        self.run_task(CountBeansTask, **options)
