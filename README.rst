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

Documentation
-------------

The full documentation is at https://django-task.readthedocs.io.

Quickstart
----------

Install Django Task::

    pip install django-task

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_task.apps.DjangoTaskConfig',
        ...
    )

Add Django Task's URL patterns:

.. code-block:: python

    from django_task import urls as django_task_urls


    urlpatterns = [
        ...
        url(r'^', include(django_task_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
