=====
Usage
=====

To use Django Task in a project, add it to your `INSTALLED_APPS`:

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
