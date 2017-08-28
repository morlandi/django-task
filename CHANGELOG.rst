0.1.2
-----
* TaskCommand.run_task() renamed as TaskCommand.run_job()
* New TaskCommand.run_task() creates a Task, then runs it;
  this guarantees that something is traced even when background job will fail

0.1.3
-----
* Polymorphic behaviour or Task.get_child() restored

0.1.4
-----
* Fix OneToOneRel import for Django < 1.9
