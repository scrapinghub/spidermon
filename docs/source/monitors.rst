====================
Monitoring your jobs
====================

Monitors
--------

Monitors are the main class where you include your monitoring logic. After defining
them, you need to include them in a `MonitorSuite`, so they can be executed.

As `spidermon.core.monitors.Monitor` inherits from Python `unittest.TestCase`, you
can use all existing assertion methods in your monitors.

In the following example, we define a monitor that will verify whether a minimum
number of items were extracted and fails if it is less than the expected threshold.

.. code-block:: python

    from spidermon import Monitor, monitors

    @monitors.name('Item count')
    class ItemCountMonitor(Monitor):

        @monitors.name('Minimum items extracted')
        def test_minimum_number_of_items_extracted(self):
            minimum_threshold = 100
            item_extracted = getattr(self.data.stats, 'item_scraped_count', 0)
            self.assertFalse(
                item_extracted < minimum_threshold,
                msg='Extracted less than {} items'.format(minimum_threshold)
            )

A :class:`~spidermon.core.monitors.Monitor` instance defines a monitor that includes
your monitoring logic and has the following properties that can be used to help you
implement your monitors:

``data.stats`` dict-like object containing the stats of the spider execution

``data.crawler`` instance of actual `Crawler`_ object

``data.spider`` instance of actual `Spider`_ object

.. _`Crawler`: https://doc.scrapy.org/en/latest/topics/api.html#scrapy.crawler.Crawler
.. _`Spider`: https://doc.scrapy.org/en/latest/topics/spiders.html?highlight=scrapy.Spider#scrapy.spiders.Spider

.. autoclass:: spidermon.core.monitors.Monitor

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

  ``monitors`` list of :class:`~spidermon.core.monitors.Monitor` that will be executed if this suite is enabled.

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

Base Stat Monitor
-----------------

Most of the monitors we create validate a numerical value from job stats against a configurable
threshold. This is a common pattern that leads us to create almost repeated code for any new monitor
we add to our projects.

To reduce the amount of boilerplate code, we have this base class that your custom monitor can
inherit from and with a few attributes you end with a full functional monitor that just needs
to be added to your Monitor Suite to be used.

.. automodule:: spidermon.contrib.scrapy.monitors
    :members: BaseStatMonitor
    :noindex:

The Basic Monitors
------------------

Spidermon has some batteries included :)

.. automodule:: spidermon.contrib.scrapy.monitors
    :members: ItemCountMonitor, ErrorCountMonitor, WarningCountMonitor, CriticalCountMonitor, FinishReasonMonitor,
              UnwantedHTTPCodesMonitor, ItemValidationMonitor, FieldCoverageMonitor,
              RetryCountMonitor, DownloaderExceptionMonitor, SuccessfulRequestsMonitor,
              TotalRequestsMonitor, PeriodicExecutionTimeMonitor, JobsComparisonMonitor

Is there a **Basic Scrapy Suite** ready to use?
------------------------------------------------

Of course, there is! We really want to make it easy for you to monitor your spiders ;)

.. automodule:: spidermon.contrib.scrapy.monitors
    :members: SpiderCloseMonitorSuite
    :noindex:

If you want only some of these monitors it's easy to create your own suite with
your own list of monitors similar to this one.

Periodic Monitors
-----------------

Sometimes we don't want to wait until the end of the spider execution to monitor
it. For example, we may want to be notified as soon the number of errors reaches
a value or close the spider if the time elapsed is greater than expected.

You define your `Monitors`_ and `Monitor Suites`_ the same way as before, but
you need to provide the time interval (in seconds) between each of the times the
`Monitor Suites`_ is run.

In the following example, we defined a periodic monitor suite that will be
executed every minute and will verify if the number of errors found is lesser
than a value. If not, the spider will be closed.

First we define a new action that will close the spider when executed:

.. code-block:: python

    # tutorial/actions.py
    from spidermon.core.actions import Action

    class CloseSpiderAction(Action):

        def run_action(self):
            spider = self.data['spider']
            spider.logger.info("Closing spider")
            spider.crawler.engine.close_spider(spider, 'closed_by_spidermon')

Then we create our monitor and monitor suite that verifies the number of errors
and then take an action if it fails:

.. code-block:: python

    # tutorial/monitors.py
    from tutorial.actions import CloseSpiderAction

    @monitors.name('Periodic job stats monitor')
    class PeriodicJobStatsMonitor(Monitor, StatsMonitorMixin):

        @monitors.name('Maximum number of errors reached')
        def test_number_of_errors(self):
            accepted_num_errors = 20
            num_errors = self.data.stats.get('log_count/ERROR', 0)

            msg = 'The job has exceeded the maximum number of errors'
            self.assertLessEqual(num_errors, accepted_num_errors, msg=msg)

    class PeriodicMonitorSuite(MonitorSuite):
        monitors = [PeriodicJobStatsMonitor]
        monitors_failed_actions = [CloseSpiderAction]

The last step is to configure the suite to be executed every 60 seconds:

.. code-block:: python

    # tutorial/settings.py

    SPIDERMON_PERIODIC_MONITORS = {
        'tutorial.monitors.PeriodicMonitorSuite': 60,  # time in seconds
    }

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
