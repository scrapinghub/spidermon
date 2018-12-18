.. _monitors:

====================
Monitoring your jobs
====================

Monitor Suites
--------------

A `Monitor Suite` groups a set of `Monitor` class and allows you to specify which
actions must be executed at specified moments of the spider execution.

Here an example of how to configure a new monitor suite in your project:

.. code-block:: python

    # monitors.py
    from spidermon.core.suites import MonitorSuite

    # Monitor definition above...
    class SpiderCloseMonitorSuite(MonitorSuite):
        monitors = [
            # (your monitors)
        ]

        monitors_finished_actions = [
            # actions to execute when suite finishes its execution
        ]

        monitors_failed_actions = [
            # actions to execute when suite finishes its execution with a failed monitor
        ]

.. code-block:: python

    # settings.py
    SPIDERMON_SPIDER_OPEN_MONITORS = (
        # list of monitor suites to be executed when the spider starts
    )

    SPIDERMON_SPIDER_CLOSE_MONITORS = (
        # list of monitor suites to be executed when the spider finishes
    )

.. class:: MonitorSuite(name=None, monitors=None, monitors_finished_actions=None, monitors_passed_actions=None, monitors_failed_actions=None, order=None, crawler=None)

  An instance of :class:`MonitorSuite` defines a set of monitors and actions to be
  executed after the job finishes its execution.

  ``name`` suite name

  ``monitors`` list of :class:`~spidermon.core.monitors.Monitor` that will be executed
  if this suite is enabled.

  ``monitors_finished_actions`` list of action classes that will be executed when
  all monitors finished their execution.

  ``monitors_passed_actions`` list of action classes that will be executed if all
  monitors passed.

  ``monitors_failed_actions`` list of action classes that will be executed if at
  least one of the monitors failed.

  ``order`` if you have more than one suite enabled in your project, this integer
  defines the order of execution of the suites

  ``crawler`` crawler instance

  .. method:: on_monitors_finished(result)

      Executed right after the monitors finished their execution and before any other
      action is executed.

      ``result`` stats of the spider execution


  .. method:: on_monitors_passed(result)

      Executed right after the monitors finished their execution but after the
      actions defined in `monitors_finished_actions` were executed if all monitors
      passed.

      ``result`` stats of the spider execution

  .. method:: on_monitors_failed(result)

      Executed right after the monitors finished their execution but after the
      actions defined in `monitors_finished_actions` were executed if at least one
      monitor failed.

      ``result`` stats of the spider execution
