Example Project for django-task
-------------------------------

This example is provided as a convenience feature to allow potential users to try the app straight from the app repo without having to create a django project.

It can also be used to develop the app in place.

To run this example, follow these instructions:

1. Navigate to the `example` directory
2. Install the requirements for the package::

    pip install -r requirements.txt

3. Make and apply migrations::

    python manage.py migrate

4. Create an account::

    python manage.py createsuperuser --username admin

5. Run at least a worker for the queue named "default", and the server::

    python manage.py rqworker example_default
    python manage.py runserver

6. Access from the browser at `http://127.0.0.1:8000`


Running unit tests for the example project
------------------------------------------

The example project contains a simple app called "tasks" which defines the required
models for a couple af simple tasks, and provides it's own unit tests.

To run these unit tests, use the following command::

    python manage.py test --settings=example.test_settings

The output should be as follows::

    RQ_QUEUES:
    {'example_default': {'URL': 'redis://localhost:6379/0', 'DEFAULT_TIMEOUT': -1}, 'example_low': {'URL': 'redis://localhost:6379/0'}, 'example_high': {'URL': 'redis://localhost:6379/0', 'DEFAULT_TIMEOUT': 500}}
    Creating test database for alias 'default'...
    System check identified no issues (0 silenced).
    .task.id: 914a7aa6-6e16-4397-9eab-05d31ed67cbb
    job.run() enter
    2019-10-14 14:42:48,170|INFO|STARTED [queue: "test_default", task: "914a7aa6-6e16-4397-9eab-05d31ed67cbb", job: "9791f6f7-74e8-4485-8f93-093536897a48"]
    2019-10-14 14:42:48,284|INFO|SUCCESS [queue: "test_default", task: "914a7aa6-6e16-4397-9eab-05d31ed67cbb", job: "9791f6f7-74e8-4485-8f93-093536897a48"]
    2019-10-14 14:42:48,285|DEBUG|params:
    {'num_beans': 10}
    job.run() leave
    job.id: 9791f6f7-74e8-4485-8f93-093536897a48
    .job.run() enter
    2019-10-14 14:42:49,439|INFO|STARTED [queue: "test_default", task: "9d7451e2-8c06-4deb-8825-ce2c3287e8e7", job: "b558a656-13ec-4a79-913d-d9d6260a6c5b"]
    2019-10-14 14:42:49,558|INFO|SUCCESS [queue: "test_default", task: "9d7451e2-8c06-4deb-8825-ce2c3287e8e7", job: "b558a656-13ec-4a79-913d-d9d6260a6c5b"]
    2019-10-14 14:42:49,558|DEBUG|params:
    {'num_beans': 10}
    job.run() leave
    Waiting for task completed:
    .
    ----------------------------------------------------------------------
    Ran 3 tests in 2.808s

    OK
    Destroying test database for alias 'default'...
