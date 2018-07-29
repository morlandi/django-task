from __future__ import print_function
import time
import redis
import logging
import traceback
from django.conf import settings
from .models import CountBeansTask
from django_task.job import Job
from rq import get_current_job


class CountBeansJob(Job):

    @staticmethod
    def execute(job, task):
        params = task.retrieve_params_as_dict()
        num_beans = params['num_beans']
        for i in range(0, num_beans):
            time.sleep(0.01)
            task.set_progress((i + 1) * 100 / num_beans, step=10)
