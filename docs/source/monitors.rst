.. _monitors:

====================
Monitoring your jobs
====================

Monitors
--------

Monitors are the main class where you include your monitoring logic. After defining
them, you need to include them in a `MonitorSuite`, so they can be executed.

As `spidermon.core.monitors.Monitor` inherits from Python `unittest.TestCase`, you
can use all existing assertion methods in your monitors.

In the following example, we define a monitor that will verify if the number of items
extracted is bigger than a specified threshold:

.. code-block:: python

    from spidermon import Monitor, monitors

    @monitors.name('Item count')
    class ItemCountMonitor(Monitor):

        @monitors.name('Check minimum number of items')
        def test_minimum_number_of_items(self):
            minimum_threshold = 100
            item_extracted = getattr(self.data.stats, 'item_scraped_count', 0)

            msg = 'Extracted less than {} items'.format(minimum_threshold)
            self.assertTrue(
                item_extracted >= minimum_threshold, msg=msg
            )

A `Monitor` instance has the following properties that can be used to help you to
implement your monitors:

``data.stats`` dict-like object containing the stats of the spider execution

``data.crawler`` instance of actual `Crawler`_ object

``data.spider`` instance of actual `Spider`_ object

.. _`Crawler`: https://doc.scrapy.org/en/latest/topics/api.html#scrapy.crawler.Crawler
.. _`Spider`: https://doc.scrapy.org/en/latest/topics/spiders.html?highlight=scrapy.Spider#scrapy.spiders.Spider

Monitor Suites
--------------

A `Monitor Suite` groups a set of `Monitor` classes and allows you to specify which
actions must be executed at specified moments of the spider execution.

Here is an example of how to configure a new monitor suite in your project:

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

What to monitor?
----------------

These are some of the usual metrics used in the monitors:

- the amount of items extracted by the spider.

- the amount of successful responses received by the spider.

- the amount of failed responses (server-side errors, network errors, proxy errors, etc.).

- the amount of requests that reach the maximum amount of retries and are finally discarded.

- the amount of time it takes to finish the crawl.

- the amount of errors in the log (spider errors, generic errors detected by Scrapy, etc.)

- the amount of bans.

- the job outcome (if it finishes without major issues or if it is closed prematurely because it detects too many bans, for example).

- the amount of items that don't contain a specific field or a set of fields

- the amount of items with validation errors (missing required fields, incorrect format, values that don't match a specific regular expression, strings that are too long/short, numeric values that are too high/low, etc.)
