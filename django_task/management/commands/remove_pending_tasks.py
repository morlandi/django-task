from django.core.management.base import BaseCommand
from django_task.utils import revoke_pending_tasks


class Command(BaseCommand):

    help = ("Revoke all pending tasks in tables")

    def handle(self, *app_labels, **options):
        counter = revoke_pending_tasks()
        print('Done. %d tasks revoked' % counter)
