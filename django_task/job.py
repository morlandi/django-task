import logging
import traceback
#from rq import get_current_job
#from .app_settings import REDIS_URL
from .app_settings import JOB_TRACE_ENABLED


def job_trace(message):
    if JOB_TRACE_ENABLED:
        print(('\x1b[1;35;40m%s\x1b[0m' % message))


class Job(object):

    @classmethod
    def run(job_class, task_class, task_id):

        from .models import TaskRQ
        from .models import TaskThreaded

        from django_task.job import job_trace

        job_trace('job.run() enter')
        task = None
        result = 'SUCCESS'
        failure_reason = ''

        try:

            # Retrieve task obj and set as Started
            task = task_class.get_task_from_id(task_id)

            if issubclass(task_class, TaskRQ):
                import redis
                from django_task.app_settings import REDIS_URL
                from rq import get_current_job
                # this raises a "Could not resolve a Redis connection" exception in sync mode
                #job = get_current_job()
                job = get_current_job(connection=redis.Redis.from_url(REDIS_URL))
                job_id = job.get_id()
            elif issubclass(task_class, TaskThreaded):
                import threading
                job = threading.current_thread()
                job_id = job.ident
            else:
                raise Exception('Unknown task_class')

            task.set_status(status='STARTED', job_id=job_id)

            # Execute job passing by task
            job_class.execute(job, task)

        except Exception as e:
            job_trace('ERROR: %s' % str(e))
            job_trace(traceback.format_exc())

            if task:
                task.log(logging.ERROR, str(e))
                task.log(logging.ERROR, traceback.format_exc())
            result = 'FAILURE'
            failure_reason = str(e)

        finally:
            if task:
                task.set_status(status=result, failure_reason=failure_reason)
            try:
                job_class.on_complete(job, task)
            except Exception as e:
                job_trace('NESTED ERROR: Job.on_completed() raises error "%s"' % str(e))
                job_trace(traceback.format_exc())
        job_trace('job.run() leave')

    @staticmethod
    def on_complete(job, task):
        pass

    @staticmethod
    def execute(job, task):
        pass
