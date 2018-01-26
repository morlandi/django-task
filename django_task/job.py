from __future__ import print_function
import redis
import logging
import traceback
from rq import get_current_job
from .app_settings import REDIS_URL


class Job(object):

    @classmethod
    def run(job_class, task_class, task_id):
        task = None
        result = 'SUCCESS'
        failure_reason = ''

        try:

            # this raises a "Could not resolve a Redis connection" exception in sync mode
            #job = get_current_job()
            job = get_current_job(connection=redis.Redis.from_url(REDIS_URL))

            # Retrieve task obj and set as Started
            task = task_class.get_task_from_id(task_id)
            task.set_status(status='STARTED', job_id=job.get_id())

            # Execute job passing by task
            job_class.execute(job, task)

        except Exception as e:
            if task:
                task.log(logging.ERROR, str(e))
                task.log(logging.ERROR, traceback.format_exc())
            result = 'FAILURE'
            failure_reason = str(e)

        finally:
            if task:
                task.set_status(status=result, failure_reason=failure_reason)

    @staticmethod
    def execute(job, task):
        pass
