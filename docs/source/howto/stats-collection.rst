.. _stats_collection:

How do I compare Spider executions?
===================================

Sometimes it is worthy to compare results from previous executions of your
spider. For example, we should be able to track whether the number of items
returned is lower than previous executions, which may indicate a problem.

Scrapy allows you to collect stats in the form key/value, but these stats are
lost when the spider finishes its execution. Spidermon provides a built-in
stats collector that stores the stats of all spider executions in your local
file system.

After enabling this stats collector, every spider instance running will have a
``stats_history`` attribute containing a list of the stats of the previous spider
executions that can be easily accessed in your monitors.

To enable it, include the following code in your project settings:

.. code-block:: python

    # tutorial/settings.py
    STATS_CLASS = (
        "spidermon.contrib.stats.statscollectors.local_storage.LocalStorageStatsHistoryCollector"
    )

    # Stores the stats of the last 10 spider execution (default=100)
    SPIDERMON_MAX_STORED_STATS = 10

The following example shows how we can verify whether the number of items
returned in the current spider execution is higher than 90% of the mean of items
returned in the previous spider executions.

.. code-block:: python

    # tutorial/monitors.py
    from spidermon import Monitor, MonitorSuite, monitors


    @monitors.name("History Validation")
    class HistoryMonitor(Monitor):

      @monitors.name("Expected number of items extracted")
      def test_expected_number_of_items_extracted(self):
          spider = self.data["spider"]
          total_previous_jobs = len(spider.stats_history)
          if total_previous_jobs == 0:
              return

          previous_item_extracted_mean = (
              sum(
                  previous_job["item_scraped_count"]
                  for previous_job in spider.stats_history
              )
              / total_previous_jobs
          )
          items_extracted = self.data.stats["item_scraped_count"]

          # Minimum number of items we expect to be extracted
          minimum_threshold = 0.9 * previous_item_extracted_mean

          self.assertFalse(
              items_extracted <= minimum_threshold,
              msg="Expected at least {} items extracted.".format(
                  minimum_threshold
              ),
          )

    class SpiderCloseMonitorSuite(MonitorSuite):
        monitors = [HistoryMonitor]

When running on `Scrapy Cloud`_ you can use ``spidermon.contrib.stats.statscollectors.sc_collections.ScrapyCloudCollectionsStatsHistoryCollector`` instead.
This will save your stats in a `collection`_ on your scrapy dashboard, named like ``{your_spider_name}_stats_history``. The rest of the sample code presented previously will work unchanged.


.. warning::
    `STATS_CLASS`_ is overriden by default in `Scrapy Cloud`_. You need to manually include ``spidermon.contrib.stats.statscollectors.sc_collections.DashCollectionsStatsHistoryCollector`` in your `spider settings`_.

.. _`STATS_CLASS`: https://docs.scrapy.org/en/latest/topics/settings.html#stats-class
.. _`spider settings`: https://support.zyte.com/support/solutions/articles/22000200670-customizing-scrapy-settings-in-scrapy-cloud
.. _`Scrapy Cloud`: https://www.zyte.com/scrapy-cloud/
.. _`DotScrapy Persistence Add-on`: https://support.zyte.com/support/solutions/articles/22000200401-dotscrapy-persistence-addon
.. _`collection`: https://docs.zyte.com/scrapy-cloud/collections.html