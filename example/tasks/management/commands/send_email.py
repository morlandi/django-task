from django_task.task_command import TaskCommand


class Command(TaskCommand):

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('sender')
        parser.add_argument('subject')
        parser.add_argument('message')
        parser.add_argument('-r', '--recipients', nargs='*')

    def handle(self, *args, **options):
        from example.models import SendEmailTask

        # transform the list of recipents into text
        # (one line for each recipient)
        options['recipients'] = '\n'.join(options['recipients']) if options['recipients'] is not None else ''

        # format multiline message
        options['message'] = options['message'].replace('\\n', '\n')

        self.run_task(SendEmailTask, **options)
