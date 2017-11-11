.. :changelog:

History
=======

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
