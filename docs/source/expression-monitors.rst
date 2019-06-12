.. _expression-monitors:

Expression Monitors
-------------------

Expressions monitors are Monitors that are created on-the-fly when the
Spidermon extension initializes.

The tests that the Expression Monitors should execute are defined as a list
of simple python expression.

Here's an example of how to declare 2 ExpressionMonitors.

The 1st monitor with 2 tests, one for checking the spider name and other test to
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

You have the following objects available to be used in your *expression*:
    
    * stats
    * crawler
    * spider
    * job
    * validation
    * responses

Each item of the list should follow this schema::

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

.. note::

    Is important to notice that not the full-set of the Python Language features 
    are available to the expressions, only the ones that makes sense for a simple
    expression that should evaluate to ``True`` or ``False``.

    To have a more deep understand about which features of the language are available
    please refer to ``spidermon.python.intrepeter.Interpreter``.
