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

SPIDERMON_ENABLED
-----------------

Default: ``False``

Whether to enable Spidermon.

SPIDERMON_EXPRESSIONS_MONITOR_CLASS
-----------------------------------

Default: ``spidermon.python.monitors.ExpressionMonitor``

A subclass of ``spidermon.python.monitors.ExpressionMonitor``.

This class will be used to generate :ref:`expression monitors<topics-expression-monitors>`.

    * `SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS`_
    * `SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS`_
    * `SPIDERMON_ENGINE_STOP_EXPRESSION_MONITORS`_

.. note::
    You probably will not change this setting unless you have an advanced use case and
    needs to change how the context data is build or how the on-the-fly ``MonitorSuite``
    are generated. Otherwise the default should be enough.

SPIDERMON_PERIODIC_MONITORS
---------------------------

Default: ``{}``

A dict containing the monitor suites that must be executed periodically as key and
the time interval (in seconds) between the executions as value.

For example, the following suite will be executed every 30 minutes:

.. code-block:: python

    SPIDERMON_PERIODIC_MONITORS = {
        'tutorial.monitors.PeriodicMonitorSuite': 1800,
    }

SPIDERMON_SPIDER_CLOSE_MONITORS
-------------------------------

Default: ``[]``

List of monitor suites to be executed when the spider closes.

SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS
------------------------------------------

Default: ``[]``

List of dictionaries describing :ref:`expression monitors<topics-expression-monitors>` to run when a spider is closed.

SPIDERMON_SPIDER_OPEN_MONITORS
------------------------------

Default: ``[]``

List of monitor suites to be executed when the spider starts.

SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS
-----------------------------------------

Default: ``[]``

List of dictionaries describing :ref:`expression monitors<topics-expression-monitors>` to run when a spider is opened.

SPIDERMON_ENGINE_STOP_MONITORS
------------------------------

List of monitor suites to be executed when the crawler engine is stopped.

SPIDERMON_ENGINE_STOP_EXPRESSION_MONITORS
-----------------------------------------
Default: ``[]``

List of dictionaries describing :ref:`expression monitors<topics-expression-monitors>` to run when the engine is stopped.

SPIDERMON_ADD_FIELD_COVERAGE
----------------------------
Default: ``False``

When enabled, Spidermon will add statistics about the number of items scraped and coverage for each existing
field following this format:

``'spidermon_item_scraped_count/<item_type>/<field_name>': <item_count>``
``'spidermon_field_coverage/<item_type>/<field_name>': <coverage>``

.. note::

   Nested fields are also supported. For example, if your spider returns these items:

   .. code-block:: python

      [
        {
          "field_1": {
            "nested_field_1_1": "value",
            "nested_field_1_2": "value",
          },
        },
        {
          "field_1": {
            "nested_field_1_1": "value",
          },
          "field_2": "value"
        },
      ]

   Statistics will be like the following:

   .. code-block:: python

      'spidermon_item_scraped_count/dict': 2,
      'spidermon_item_scraped_count/dict/field_1': 2,
      'spidermon_item_scraped_count/dict/field_1/nested_field_1_1': 2,
      'spidermon_item_scraped_count/dict/field_1/nested_field_1_2': 1,
      'spidermon_item_scraped_count/dict/field_2': 1,
      'spidermon_field_coverage/dict/field_1': 1,
      'spidermon_field_coverage/dict/field_1/nested_field_1_1': 1,
      'spidermon_field_coverage/dict/field_1/nested_field_1_2': 0.5,
      'spidermon_item_scraped_count/dict/field_2': 0.5,

SPIDERMON_FIELD_COVERAGE_SKIP_NONE
----------------------------------
Default: ``False``

When enabled, returned fields that have ``None`` as value will not be counted as fields with a value.

Considering your spider returns the following items:

.. code-block:: python

   [
     {
       "field_1": None,
       "field_2": "value",
     },
     {
       "field_1": "value",
       "field_2": "value",
     },
   ]

If this setting is set to ``True``, spider statistics will be:

.. code-block:: python

   'spidermon_item_scraped_count/dict': 2,
   'spidermon_item_scraped_count/dict/field_1': 1,  # Ignored None value
   'spidermon_item_scraped_count/dict/field_2': 2,
   'spidermon_field_coverage/dict/field_1': 0.5,  # Ignored None value
   'spidermon_item_scraped_count/dict/field_2': 1,

If this setting is not provided or set to ``False``, spider statistics will be:

.. code-block:: python

   'spidermon_item_scraped_count/dict': 2,
   'spidermon_item_scraped_count/dict/field_1': 2,  # Did not ignore None value
   'spidermon_item_scraped_count/dict/field_2': 2,
   'spidermon_field_coverage/dict/field_1': 1,  # Did not ignore None value
   'spidermon_item_scraped_count/dict/field_2': 1,

SPIDERMON_LIST_FIELDS_COVERAGE_LEVELS
-------------------------------------
Default: ``0``

If larger than 0, field coverage will be computed for items inside fields that are lists.
The number represents how deep in the objects tree the coverage is computed.
Be aware that enabling this might have a significant impact in performance.

Considering your spider returns the following items:

.. code-block:: python

   [
      {
          "field_1": None,
          "field_2": [{"nested_field1": "value", "nested_field2": "value"}],
      },
      {
          "field_1": "value",
          "field_2": [
              {"nested_field2": "value", "nested_field3": {"deeper_field1": "value"}}
          ],
      },
      {
          "field_1": "value",
          "field_2": [
              {
                  "nested_field2": "value",
                  "nested_field4": [
                      {"deeper_field41": "value"},
                      {"deeper_field41": "value"},
                  ],
              }
          ],
      },
   ]

If this setting is not provided or set to ``0``, spider statistics will be:

.. code-block:: python

  'item_scraped_count': 3,
  'spidermon_item_scraped_count': 3,
  'spidermon_item_scraped_count/dict': 3,
  'spidermon_item_scraped_count/dict/field_1': 3,
  'spidermon_item_scraped_count/dict/field_2': 3

If set to ``1``, spider statistics will be:

.. code-block:: python

  'item_scraped_count': 3,
  'spidermon_item_scraped_count': 3,
  'spidermon_item_scraped_count/dict': 3,
  'spidermon_item_scraped_count/dict/field_1': 3,
  'spidermon_item_scraped_count/dict/field_2': 3,
  'spidermon_item_scraped_count/dict/field_2/_items': 3,
  'spidermon_item_scraped_count/dict/field_2/_items/nested_field1': 1,
  'spidermon_item_scraped_count/dict/field_2/_items/nested_field2': 3,
  'spidermon_item_scraped_count/dict/field_2/_items/nested_field3': 1,
  'spidermon_item_scraped_count/dict/field_2/_items/nested_field3/deeper_field1': 1,
  'spidermon_item_scraped_count/dict/field_2/_items/nested_field4': 1

If set to ``2``, spider statistics will be:

.. code-block:: python

  'item_scraped_count': 3,
  'spidermon_item_scraped_count': 3,
  'spidermon_item_scraped_count/dict': 3,
  'spidermon_item_scraped_count/dict/field_1': 3,
  'spidermon_item_scraped_count/dict/field_2': 3,
  'spidermon_item_scraped_count/dict/field_2/_items': 3,
  'spidermon_item_scraped_count/dict/field_2/_items/nested_field1': 1,
  'spidermon_item_scraped_count/dict/field_2/_items/nested_field2': 3,
  'spidermon_item_scraped_count/dict/field_2/_items/nested_field3': 1,
  'spidermon_item_scraped_count/dict/field_2/_items/nested_field3/deeper_field1': 1,
  'spidermon_item_scraped_count/dict/field_2/_items/nested_field4': 1,
  'spidermon_item_scraped_count/dict/field_2/_items/nested_field4/_items': 2,
  'spidermon_item_scraped_count/dict/field_2/_items/nested_field4/_items/deeper_field41': 2

SPIDERMON_DICT_FIELDS_COVERAGE_LEVELS
-------------------------------------
Default: ``-1``

If -1, all levels of nested dictionaries will have their cover computed.

If larger than -1, field coverage will be computed for that many levels of nested dictionaries.

Considering the spider returns the following items:

  .. code-block:: python

    [
      {
          "field1": {"field1.1": "value1.1"},
          "field2": "value2",
          "field3": {"field3.1": "value3.1"},
          "field4": {
              "field4.1": {
                  "field4.1.1": "value",
                  "field4.1.2": "value",
                  "field4.1.3": {"field4.1.3.1": "value"},
              }
          },
      },
      {
          "field1": {
              "field1.1": "value1.1",
              "field1.2": "value1.2",
          },
          "field2": "value2",
      },
    ]

  If set to ``-1``, the statistics will include:

  .. code-block:: python

      'spidermon_item_scraped_count/dict': 2
      'spidermon_item_scraped_count/dict/field1': 2
      'spidermon_item_scraped_count/dict/field1/field1.1': 2
      'spidermon_item_scraped_count/dict/field1/field1.2': 1
      'spidermon_item_scraped_count/dict/field2': 2
      'spidermon_item_scraped_count/dict/field3': 1
      'spidermon_item_scraped_count/dict/field4': 1
      'spidermon_item_scraped_count/dict/field4/field4.1': 1
      'spidermon_item_scraped_count/dict/field4/field4.1/field4.1.1': 1
      'spidermon_item_scraped_count/dict/field4/field4.1/field4.1.2': 1
      'spidermon_item_scraped_count/dict/field4/field4.1/field4.1.3': 1
      'spidermon_item_scraped_count/dict/field4/field4.1/field4.1.3/field4.1.3.1': 1

  If set to ``0``, the statistics will include:

  .. code-block:: python

      'spidermon_item_scraped_count/dict': 2
      'spidermon_item_scraped_count/dict/field1': 2
      'spidermon_item_scraped_count/dict/field2': 2
      'spidermon_item_scraped_count/dict/field3': 1
      'spidermon_item_scraped_count/dict/field4': 1

  If set to ``1``, the statistics will include:

  .. code-block:: python

      'spidermon_item_scraped_count/dict': 2
      'spidermon_item_scraped_count/dict/field1': 2
      'spidermon_item_scraped_count/dict/field1/field1.1': 2
      'spidermon_item_scraped_count/dict/field1/field1.2': 1
      'spidermon_item_scraped_count/dict/field2': 2
      'spidermon_item_scraped_count/dict/field3': 1
      'spidermon_item_scraped_count/dict/field4': 1
      'spidermon_item_scraped_count/dict/field4/field4.1': 1
      'spidermon_item_scraped_count/dict/field4/field4.1/field4.1.1': 1

  If set to ``2``, the statistics will include:

  .. code-block:: python

      'spidermon_item_scraped_count/dict': 2
      'spidermon_item_scraped_count/dict/field1': 2
      'spidermon_item_scraped_count/dict/field1/field1.1': 2
      'spidermon_item_scraped_count/dict/field1/field1.2': 1
      'spidermon_item_scraped_count/dict/field2': 2
      'spidermon_item_scraped_count/dict/field3': 1
      'spidermon_item_scraped_count/dict/field4': 1
      'spidermon_item_scraped_count/dict/field4/field4.1': 1
      'spidermon_item_scraped_count/dict/field4/field4.1/field4.1.1': 1
      'spidermon_item_scraped_count/dict/field4/field4.1/field4.1.2': 1
      'spidermon_item_scraped_count/dict/field4/field4.1/field4.1.3': 1

SPIDERMON_MONITOR_SKIPPING_RULES
--------------------------------
Default: ``None``

A dictionary where keys represent the names of the monitors to be skipped, and the corresponding values are lists containing either method names or lists defining skip conditions.

When defining skip rules based on values, the list must follow the pattern: 

``["stats_name", "comparison_operator", "threshold_value"]``. 

Here, ``stat_name`` refers to the name of the Scrapy Stat being evaluated, ``comparison_operator`` indicates the type of comparison to perform (e.g., "==", "<", ">="), and ``threshold_value`` sets the threshold for the comparison.

Additionally, custom skip rules can be defined using Python functions. These functions should accept a single argument (typically named ``monitor``) representing the monitor being evaluated and return a boolean value indicating whether the monitor should be skipped (``True``) or not (``False``).

Below are examples illustrating how skip rules can be configured in the settings.

Example #1: Skip monitor based on stat values

   .. code-block:: python

       class QuotesSpider(scrapy.Spider):
           name = "quotes"
           custom_settings = {
               "SPIDERMON_FIELD_COVERAGE_RULES": {
                   "dict/quote": 1,
                   "dict/author": 1,
               },
               "SPIDERMON_MONITOR_SKIPPING_RULES": {
                   "Field Coverage Monitor": [["item_scraped_count", "==", 0]],
               }
           }

Example #2: Skip monitor based on a custom function

   .. code-block:: python

       def skip_function(monitor):
           return datetime.datetime.today().weekday() == 4  # Don't test on Fridays

       class QuotesSpider(scrapy.Spider):
           name = "quotes"

           custom_settings = {
               "SPIDERMON_FIELD_COVERAGE_RULES": {
                   "dict/quote": 1,
                   "dict/author": 1,
               },
               "SPIDERMON_MONITOR_SKIPPING_RULES": {
                   "Field Coverage Monitor": [skip_function],
               }
           }

