Example Project for django-task
-------------------------------

This example is provided as a convenience feature to allow potential users to try the app straight from the app repo without having to create a django project.

It can also be used to develop the app in place.

To run this example, follow these instructions:

1. Navigate to the `example` directory
2. Install the requirements for the package::

    pip install -r requirements.txt

3. Make and apply migrations::

    python manage.py makemigrations
    python manage.py migrate

4. Create an account::

    python manage.py createsuperuser --username admin

5. Run at least a worker for the queue named "default", and the server::

    python manage.py rqworker example_default
    python manage.py runserver

6. Access from the browser at `http://127.0.0.1:8000`
