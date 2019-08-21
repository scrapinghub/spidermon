.. _topics-settings:

========
Settings
========

The Spidermon settings allow you to customize the behaviour of your monitors
enabling, disabling and configuring features like enabled monitors, monitor
actions, item validation and notifications.

.. _topics-settings-ref:

Built-in settings reference
===========================

Here's a list of all available Spidermons settings, in alphabetical order, along
with their default values and the scope where they apply. These settings must
be defined in `settings.py` file of your Scrapy project.

.. _SPIDERMON_ENABLED:

SPIDERMON_ENABLED
-----------------

Default: ``False``

Whether to enable Spidermon.

.. _SPIDERMON_EXPRESSIONS_MONITOR_CLASS:

SPIDERMON_EXPRESSIONS_MONITOR_CLASS
-----------------------------------


Default: ``spidermon.python.monitors.ExpressionMonitor``

A subclass of ``spidermon.python.monitors.ExpressionMonitor``.

This class will be used to generate :ref:`expression monitors<topics-expression-monitors>`.

    * :ref:`SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS`
    * :ref:`SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS`
    * :ref:`SPIDERMON_ENGINE_STOP_EXPRESSION_MONITORS`

.. note::
    You probably will not change this setting unless you have an advanced use case and
    needs to change how the context data is build or how the on-the-fly ``MonitorSuite``
    are generated. Otherwise the default should be enough.

.. _SPIDERMON_PERIODIC_MONITORS:

SPIDERMON_PERIODIC_MONITORS
---------------------------

Default: ``{}``

A dict containing the monitor suites that must be executed periodically as key and
the time interval (in seconds) between the executions as value.

For example, the following suite will be executed every 30 minutes:

.. code-block:: python

    SPIDERMON_PERIODIC_MONITORS = {
        'myproject.monitors.PeriodicMonitorSuite': 1800,
    }

.. _SPIDERMON_SPIDER_CLOSE_MONITORS:

SPIDERMON_SPIDER_CLOSE_MONITORS
-------------------------------

Default: ``[]``

List of monitor suites to be executed when the spider closes.

.. _SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS:

SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS
------------------------------------------

Default: ``[]``

List of dictionaries describing :ref:`expression monitors<topics-expression-monitors>` to run when a spider is closed.

.. _SPIDERMON_SPIDER_OPEN_MONITORS:

SPIDERMON_SPIDER_OPEN_MONITORS
------------------------------

Default: ``[]``

List of monitor suites to be executed when the spider starts.

.. _SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS:

SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS
-----------------------------------------

Default: ``[]``

List of dictionaries describing :ref:`expression monitors<topics-expression-monitors>` to run when a spider is opened.

.. _SPIDERMON_ENGINE_STOP_MONITORS:

SPIDERMON_ENGINE_STOP_MONITORS
------------------------------

List of monitor suites to be executed when the crawler engine is stopped.


.. _SPIDERMON_ENGINE_STOP_EXPRESSION_MONITORS:

SPIDERMON_ENGINE_STOP_EXPRESSION_MONITORS
-----------------------------------------
Default: ``[]``

List of dictionaries describing :ref:`expression monitors<topics-expression-monitors>` to run when the engine is stopped.
