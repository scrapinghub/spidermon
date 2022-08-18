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

SPIDERMON_FIELD_COVERAGE_SKIP_WITHOUT_FIELD_COVERAGE_RULES
----------------------------
Default: ``False``

When enabled, Spidermon will add statistics about the number of items scraped and coverage only for fields that
exist in setting SPIDERMON_FIELD_COVERAGE_RULES in following format:

``'spidermon_item_scraped_count/<item_type>/<field_name>': <item_count>``
``'spidermon_field_coverage/<item_type>/<field_name>': <coverage>``

Using this setting will help to limit number of records in statistic in case of huge number of fields (>500)
in the item.

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
        {
          "field_1": {
            "nested_field_1_2": "value",
          },
          "field_2": "value"
        },
        {
          "field_3": {
            "nested_field_1_1": "value",
          },
        },
      ]

    and you have these rules:

   .. code-block:: python

    # project/settings.py
    SPIDERMON_FIELD_COVERAGE_RULES = {
        "dict/field_1": 0.75,
        "dict/field_1/field_1_1": 0.5,
        "dict/field_2": 1.0,
    }


   Statistics will be like the following (only includes fields from setting SPIDERMON_FIELD_COVERAGE_RULES):

   .. code-block:: python

      'spidermon_item_scraped_count/dict': 4,
      'spidermon_item_scraped_count/dict/field_1': 3,
      'spidermon_item_scraped_count/dict/field_1/nested_field_1_1': 2,
      'spidermon_item_scraped_count/dict/field_2': 2,

      'spidermon_field_coverage/dict/field_1': 0.75,
      'spidermon_field_coverage/dict/field_1/nested_field_1_1': 0.5,
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
