.. _topics-expression-monitors:

====================
Expression Monitors
====================

Expressions Monitors are :ref:`monitors<monitors>` created on-the-fly when Spidermon extension
initializes. They can create tests based on simple expressions defined in a dictionary in
your settings like::

    SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS = [
        {
            "name": "DumbChecksMonitor",
            "tests": [
                {
                    "name": "test_spider_name",
                    "expression": "spider.name == 'httpbin'",
                },
            ],
        },
    ]

The definition of each monitor should follow the :ref:`expression-monitor-schema`.

Use the following settings to configure expression monitors:

    * :ref:`SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS`
    * :ref:`SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS`
    * :ref:`SPIDERMON_ENGINE_STOP_EXPRESSION_MONITORS`

You have the following objects available to be used in your *expression*:

    * stats
    * crawler
    * spider
    * job
    * validation
    * responses

.. note::

    Notice that not the full-set of the Python Language features are available
    to the expressions, only the ones that makes sense for a simple expressions
    that should evaluate to ``True`` or ``False``.

    To have a more deep understand about which features of the language are available
    please refer to ``spidermon.python.interpreter.Interpreter``.


.. _how-to-create-expression-monitor:

How to create an expression monitor
===================================

First you need to choose *when* you want to run your expression monitors.

You can use :ref:`SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS` to run a monitor
when a spider opens, or :ref:`SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS` if you
want to run a monitor when a spider is closed.

There's also the :ref:`SPIDERMON_ENGINE_STOP_EXPRESSION_MONITORS` setting to run a monitor
once the engine has stopped.

Here's an example of how to declare two ``ExpressionMonitors``.

The first monitor with two tests, one for checking the spider name and other test to
check if the crawler is there. The 2nd monitor will check if the spider
finished with ``finished``::

    [
        {
            "name": "DumbChecksMonitor",
            "description": "My expression monitor",
            "tests": [
                {
                    "name": "test_spider_name",
                    "description": "Test spider name",
                    "expression": "spider.name == 'httpbin'",
                },
                {
                    "name": "test_crawler_exists",
                    "description": "Test Crawler exists",
                    "expression": "crawler is not None"
                }
            ],
        },
        {
            "name": "FinishedOkMonitor",
            "description": "My expression monitor 2",
            "tests": [
                {
                    "name": "test_finish_reason",
                    "description": "Test finish reason",
                    "expression": 'stats["finish_reason"] == "finished"',
                }
            ],
        }
    ]


.. _expression-monitor-schema:

Expression monitor schema
=========================

Each `expression monitor` should follow this schema::

    {
       "type": "object",
       "properties": {
           "name": {"type": "string", "minLength": 1},
           "description": {"type": "string", "minLength": 1},
           "tests": {
               "type": "array",
               "items": {
                   "type": "object",
                   "properties": {
                       "name": {"type": "string", "minLength": 1},
                       "description": {"type": "string", "minLength": 1},
                       "expression": {"type": "string", "minLength": 1},
                       "fail_reason": {"type": "string", "minLength": 1},
                   },
                   "required": ["name", "expression"],
               },
           },
       },
       "required": ["name", "tests"],
     }

