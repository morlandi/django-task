=============================
Django Task
=============================

.. image:: https://badge.fury.io/py/django-task.svg
    :target: https://badge.fury.io/py/django-task

.. image:: https://travis-ci.org/morlandi/django-task.svg?branch=master
    :target: https://travis-ci.org/morlandi/django-task

.. image:: https://codecov.io/gh/morlandi/django-task/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/morlandi/django-task

A Django app to run new background tasks from either admin or cron, and inspect task history from admin

Quickstart
----------

Install Django Task::

    pip install django-task

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_rq',
        'django_task',
        ...
    )

Add Django Task's URL patterns:

.. code-block:: python

    urlpatterns = [
        ...
        url(r'^django_task/', include('django_task.urls', namespace='django_task')),
        ...
    ]

Features
--------

**Purposes**

    - create async tasks programmatically
    - create and monitor async tasks from admin
    - log all tasks in the database for later inspection

**Details**

1. each specific job is described my a Model derived from models.Task, which
   is responsible for:

    - selecting the name for the consumer queue among available queues
    - collecting and saving all parameters required by the associated job
    - running the specific job asyncronously

2. a new job can be run either:

    - creating a Task from the Django admin
    - creating a Task from code, then calling Task.run()

3. job execution workflow:

    - job execution is triggered by task.run(async)
    - job will receive the task.id, and retrieve paramerts from it (task.retrieve_params_as_dict())
    - on start, job will update task status to 'STARTED' and save job.id for reference
    - during execution, the job can update the progress indicator
    - on completion, task status is finally updated to either 'SUCCESS' or 'FAILURE'
    - See example.jobs.count_beans for an example

**Execute**

Run consumer:

.. code:: bash

    python manage.py runserver


Run worker(s):

.. code:: bash

    python manage.py rqworker low high default
    python manage.py rqworker low high default
    ...

**Howto separate jobs for different instances on the same machine**

To sepatare jobs for different instances on the same machine (or more precisely
for the same redis connection), override queues names for each instance;

for example:

.. code:: python

    # file "settings.py"

    #
    # RQ config
    #

    SESSION_COOKIE_NAME = 'primary_sid'

    REDIS_URL = 'redis://localhost:6379/0'
    RQ_PREFIX = "primary_"
    QUEUE_DEFAULT = RQ_PREFIX + 'default'
    ...

    RQ_QUEUES = {
        QUEUE_DEFAULT: {
            'URL': REDIS_URL,
            'DEFAULT_TIMEOUT': 360,
        },
        ...
    }

    RQ_SHOW_ADMIN_LINK = True

then run worker as follows:

.. code:: python

    python manage.py rqworker primary_default

**Howto schedule jobs with cron**

Call management command 'count_beans', which in turn executes the required job.

For example::

    SHELL=/bin/bash
    PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

    0 * * * *  {{username}}    timeout 55m {{django.pythonpath}}/python {{django.website_home}}/manage.py count_beans 1000 >> {{django.logto}}/cron.log 2>&1

A base class TaskCommand has been provided to simplify the creation of any specific
task-related management commad;

a derived management command is only responsible for:

- defining suitable command-line parameters
- selecting the specific Task class and job function

for example:

.. code:: python

    from django_task.task_command import TaskCommand


    class Command(TaskCommand):

        def add_arguments(self, parser):
            super(Command, self).add_arguments(parser)
            parser.add_argument('num_beans', type=int)

        def handle(self, *args, **options):
            from tasks.models import CountBeansTask
            self.run_task(CountBeansTask, **options)

Screenshots
-----------

.. image:: example/etc/screenshot_001.png

.. image:: example/etc/screenshot_002.png


App settings
------------

DJANGOTASK_LOG_ROOT
    Path for log files.

    Default: None

    Example: os.path.abspath(os.path.join(BASE_DIR, '..', 'protected', 'tasklog'))

DJANGOTASK_ALWAYS_EAGER

    When True, all task are execute syncronously (useful for debugging and unit testing).

    Default: False


Running Tests
-------------

* TODO

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

References:

- `A simple app that provides django integration for RQ (Redis Queue) <https://github.com/ui/django-rq>`_
- `Asynchronous tasks in django with django-rq <https://spapas.github.io/2015/01/27/async-tasks-with-django-rq/>`_
- `django-rq redux: advanced techniques and tools <https://spapas.github.io/2015/09/01/django-rq-redux/>`_
- `Benchmark: Shared vs. Dedicated Redis Instances <https://redislabs.com/blog/benchmark-shared-vs-dedicated-redis-instances/>`_

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
