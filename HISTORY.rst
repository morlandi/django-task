.. :changelog:

History
=======

v0.3.10
-------
* Update requirements (django-rq>=1.2.0)

v0.3.9
------
* Rename `async` to `is_async` to support Python 3.7

0.1.12
------
* Deferred Task retrieval to avoid job vs. Task race condition
* Improved Readme

0.1.11
------
* superuser can view all tasks, while other users have access to their own tasks only
* js fix

0.1.10
------
* prevent task.failure_reason overflow

0.1.9
-----
* app settings

0.1.8
-----
* always start job from task.run() to prevent any possible race condition
* task.run(async) can now accept async=False

0.1.7
-----
* javascript: use POST to retrieve tasks state for UI update to prevent URL length limit exceed

0.1.6
-----
* Improved ui for TaskAdmin
* Fix unicode literals for Python3

0.1.5
-----
* fixes for Django 1.10
* send_email management command example added

0.1.4
-----
* Fix OneToOneRel import for Django < 1.9

0.1.3
-----
* Polymorphic behaviour or Task.get_child() restored

0.1.2
-----
* TaskCommand.run_task() renamed as TaskCommand.run_job()
* New TaskCommand.run_task() creates a Task, then runs it;
  this guarantees that something is traced even when background job will fail
