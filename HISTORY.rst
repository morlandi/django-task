.. :changelog:

History
=======

v1.3.5
------
* Readme updated

v1.3.4
------
* javascript helper views
* fix Task.set_progress(0)

v1.3.3
------
* make sure fields are unique in TaskAdmin fieldsets

v1.3.1
------
* unit tests verified with Python 2.7/3.6/3.7 and Django 1.10/2.0

v1.3.0
------
* cleanup
* classify as production/stable

v1.2.5
------
* Tested with Django 2.0 and Python 3.7
* Rename `async` to `is_async` to support Python 3.7
* DJANGOTASK_REJECT_IF_NO_WORKER_ACTIVE_FOR_QUEUE app setting added
* example cleanup

v1.2.4
------
* API to create and run task via ajax

v1.2.3
------
* TaskAdmin: postpone autorun to response_add() to have M2M task parameters (if any) ready
* Task.clone() supports M2M parameters

v1.2.2
------
* property to change verbosity dinamically

v1.2.1
------
* util revoke_pending_tasks() added

v1.2.0
------
* DJANGOTASK_JOB_TRACE_ENABLED setting added to enable low level tracing in Job.run()
* Added missing import in utils.py

v1.1.3
------
* cleanup: remove get_child() method being Task an abstract class
* fix: skip Task model (being abstract) in dump_all_tasks and delete_all_tasks management commands
* generic get_model_from_id() helper
* Job.on_complete() callback

v1.1.2
------
* provide list of pending and completed task status

v1.1.0
------
* INCOMPATIBLE CHANGE: Make model Task abstract for better listing performances
* redundant migrations removed
* convert request.body to string for Python3
* pretty print task params in log when task completes

v0.3.8
------
* return verbose name as description

v0.3.7
------
* description added to Task model

v0.3.6
------
* More fixes

v0.3.5
------
* log to field fix

v0.3.4
------
* log quickview + view

v0.3.3
------
* Optionally log to either file or text field
* Management commands to dump and delete all tasks

v0.3.2
------
* search by task.id and task.job_id

v0.3.1
------
* Keep track of task mode (sync or async)

v0.3.0
------
* new class Job provided to share task-related logic among job funcs

v0.2.0
------
* fixes for django 2.x

v0.1.15
-------
* hack for  prepopulated_fields

v0.1.14
-------
* css fix

v0.1.13
-------
* minor fixes

v0.1.12
------
* Deferred Task retrieval to avoid job vs. Task race condition
* Improved Readme

v0.1.11
-------
* superuser can view all tasks, while other users have access to their own tasks only
* js fix

v0.1.10
-------
* prevent task.failure_reason overflow

v0.1.9
------
* app settings

v0.1.8
------
* always start job from task.run() to prevent any possible race condition
* task.run(async) can now accept async=False

v0.1.7
------
* javascript: use POST to retrieve tasks state for UI update to prevent URL length limit exceed

v0.1.6
------
* Improved ui for TaskAdmin
* Fix unicode literals for Python3

v0.1.5
------
* fixes for Django 1.10
* send_email management command example added

v0.1.4
------
* Fix OneToOneRel import for Django < 1.9

v0.1.3
------
* Polymorphic behaviour or Task.get_child() restored

v0.1.2
------
* TaskCommand.run_task() renamed as TaskCommand.run_job()
* New TaskCommand.run_task() creates a Task, then runs it;
  this guarantees that something is traced even when background job will fail
