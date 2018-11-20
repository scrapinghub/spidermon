Getting started
===============

Spidermon is a monitoring tool for Scrapy spiders that allows you to write monitors that may
validate the execution and the results of your spiders.

This tutorial shows how to set up Spidermon to monitor a spider to check if it extracted a minimum
number of items and if they follow a defined data model. The results of the spider execution
will be sent to a Slack channel.

It is expected that you have a basic knowledge of Scrapy_. If that is not the case read the
`Scrapy Tutorial`_ and come back later. We will also assume that Spidermon is already installed on
your system. If that is not the case case, see :ref:`installation`.

.. _`Scrapy`: https://scrapy.org/
.. _`Scrapy Tutorial`: https://doc.scrapy.org/en/latest/intro/tutorial.html
.. _`Scrapy project`: https://doc.scrapy.org/en/latest/intro/tutorial.html?#creating-a-project

Our spider
----------

We are going to scrape `quotes.toscrape.com <http://quotes.toscrape.com/>`_, a website
that lists quotes from famous authors. First we
need a regular `Scrapy project`_ and create a simple spider:

.. code-block:: console

    $ scrapy startproject tutorial
    $ cd tutorial
    $ scrapy genspider quotes quotes.com

.. code-block:: python

    # tutorial/spiders/quotes.py
    import scrapy

    class QuotesSpider(scrapy.Spider):
        name = 'quotes'
        allowed_domains = ['quotes.toscrape.com']
        start_urls = ['http://quotes.toscrape.com/']

        def parse(self, response):
            for quote in response.css('.quote'):
                yield {
                    'quote': quote.css('.text::text').get(),
                    'author': quote.css('.author::text').get(),
                    'author_url': response.urljoin(
                        quote.css('.author a::attr(href)').get()),
                    'tags': quote.css('.tag *::text').getall(),
                }

            yield scrapy.Request(
                response.urljoin(
                    response.css('.next a::attr(href)').get()
                )
            )

Enabling Spidermon
------------------

To enable Spidermon in your project include the following lines in your Scrapy project
`settings.py` file:

.. code-block:: python

    SPIDERMON_ENABLED = True

    EXTENSIONS = {
        'spidermon.contrib.scrapy.extensions.Spidermon': 500,
    }

Our first monitor
-----------------

Monitors are similar to test cases with a set of methods that are executed at well defined
moments of the spider execution where you can include your monitoring logic.

Monitors are grouped into Monitor Suites which define a list of monitors that will be executed and
the actions that needs to be performed before and after the suite execute all monitors.

Our first monitor will check whether at least 10 items were returned at the end of the spider
execution.

Create a new file called `monitors.py`, where you will define and configure your monitors.

.. code-block:: python

    # monitors.py
    from spidermon import Monitor, MonitorSuite, monitors
    from spidermon.contrib.monitors.mixins import StatsMonitorMixin

    @monitors.name('Item count')
    class ItemCountMonitor(Monitor, StatsMonitorMixin):

        @monitors.name('Minimum number of items')
        def test_minimum_number_of_items(self):
            item_extracted = getattr(self.stats, 'item_scraped_count', 0)
            minimum_threshold = 10

            msg = 'Extracted less than {} items'.format(minimum_threshold)
            self.assertTrue(
                item_extracted >= minimum_threshold, msg=msg
            )

    class SpiderCloseMonitorSuite(MonitorSuite):
        monitors = [
            ItemCountMonitor,
        ]

To enable the MonitorSuite defined above, you need to set the SPIDERMON_SPIDER_CLOSE_MONITORS
list in your `settings.py` file as follows:

.. code-block:: python

    SPIDERMON_SPIDER_CLOSE_MONITORS = (
        'tutorial.monitors.SpiderCloseMonitorSuite',
    )

After executing the spider, you should see the following in your logs:

.. code-block:: console

    INFO: [Spidermon] ------------------------- MONITORS -------------------------
    INFO: [Spidermon] Item count/Minimum number of items... OK
    INFO: [Spidermon] ------------------------------------------------------------
    INFO: [Spidermon] 1 monitor in 0.001s
    INFO: [Spidermon] OK
    INFO: [Spidermon] --------------------- FINISHED ACTIONS ---------------------
    INFO: [Spidermon] ------------------------------------------------------------
    INFO: [Spidermon] 0 actions in 0.000s
    INFO: [Spidermon] OK
    INFO: [Spidermon] ---------------------- PASSED ACTIONS ----------------------
    INFO: [Spidermon] ------------------------------------------------------------
    INFO: [Spidermon] 0 actions in 0.000s
    INFO: [Spidermon] OK
    INFO: [Spidermon] ---------------------- FAILED ACTIONS ----------------------
    INFO: [Spidermon] ------------------------------------------------------------
    INFO: [Spidermon] 0 actions in 0.000s
    INFO: [Spidermon] OK
    [scrapy.statscollectors] INFO: Dumping Scrapy stats:

When the monitor fails, you will see the information of the monitor that failed in the logs like:

.. code-block:: console

    INFO: [Spidermon] ------------------------- MONITORS -------------------------
    INFO: [Spidermon] Item count/Minimum number of items... FAIL
    INFO: [Spidermon] ------------------------------------------------------------
    ERROR: [Spidermon]
    ======================================================================
    FAIL: Item count/Minimum number of items
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/renne/projects/scrapinghub/spidermon/tmp/tutorial/tutorial/monitors.py",
        line 17, in test_minimum_number_of_items
        item_extracted >= minimum_threshold, msg=msg
    AssertionError: False is not true : Extracted less than 10 items
    INFO: [Spidermon] 1 monitor in 0.001s
    INFO: [Spidermon] FAILED (failures=1)
    INFO: [Spidermon] --------------------- FINISHED ACTIONS ---------------------
    INFO: [Spidermon] ------------------------------------------------------------
    INFO: [Spidermon] 0 actions in 0.000s
    INFO: [Spidermon] OK
    INFO: [Spidermon] ---------------------- PASSED ACTIONS ----------------------
    INFO: [Spidermon] ------------------------------------------------------------
    INFO: [Spidermon] 0 actions in 0.000s
    INFO: [Spidermon] OK
    INFO: [Spidermon] ---------------------- FAILED ACTIONS ----------------------
    INFO: [Spidermon] ------------------------------------------------------------
    INFO: [Spidermon] 0 actions in 0.000s
    INFO: [Spidermon] OK

Slack notifications
-------------------

Inside a monitor suite you may define actions that are executed before or after your monitors are
executed. Spidermon has some built-in actions but you are free to define your own.

In this example, we will configure a built-in Spidermon action that sends a pre-defined message to
a Slack channel using a bot when a monitor fails.

.. code-block:: python

    # monitors.py
    from spidermon.contrib.actions.slack.notifiers import SendSlackMessageSpiderFinished

    # (...your monitors code...)

    class SpiderCloseMonitorSuite(MonitorSuite):
        monitors = [
            ItemCountMonitor,
        ]

        monitors_failed_actions = [
            SendSlackMessageSpiderFinished,
        ]

After enabling the action you need to provide the `Slack credentials`_ in your `settings.py`
file as follows:

.. code-block:: python

    SPIDERMON_SLACK_SENDER_TOKEN = '<SLACK_SENDER_TOKEN>'
    SPIDERMON_SLACK_SENDER_NAME = '<SLACK_SENDER_NAME>'
    SPIDERMON_SLACK_RECIPIENTS = ['@yourself', '#yourprojectchannel']

.. _`Slack credentials`: https://api.slack.com/docs/token-types

Item validation
---------------

Validators define the expected structure of the items.

Spidermon allows you to choose between schematics or JSON-Schema to validate your items.

.. code-block:: python

    import scrapy

    class QuoteItem(scrapy.Item):
        quote = scrapy.Field()
        author = scrapy.Field()
        author_url = scrapy.Field()
        tags = scrapy.Field()


.. code-block:: python

    from schematics.models import Model
    from schematics.types import URLType, StringType, ListType


    class QuoteItem(Model):
        quote = StringType(required=True)
        author = StringType(required=True)
        author_url = URLType(required=True)
        tags = ListType(StringType)


.. code-block:: python

    # monitors.py

    # (...other monitors...)

    @monitors.name('Item validation')
    class ItemValidationMonitor(Monitor, StatsMonitorMixin):

        @monitors.name('No item validation errors')
        def test_no_item_validation_errors(self):
            validation_errors = getattr(
                self.data.stats, 'spidermon/validation/fields/errors', 0
            )
            self.assertEqual(
                validation_errors,
                0,
                msg='Found validation errors in {} fields'.format(validation_errors)
            )

            self.data.stats


    class SpiderCloseMonitorSuite(MonitorSuite):
        monitors = [
            ItemCountMonitor,
            ItemValidationMonitor,
        ]

        monitors_failed_actions = [
            SendSlackMessageSpiderFinished,
        ]


.. code-block:: python

    ITEM_PIPELINES = {
        'spidermon.contrib.scrapy.pipelines.ItemValidationPipeline': 800,
    }

    SPIDERMON_VALIDATION_MODELS = (
        'tutorial.validators.QuoteItem',
    )





As you can see in the
[code for this tutorial](http://github.com/stummjr/spidermon-reddit-example), the
`reddit` spider generates `NewsItem` objects with the scraped data:

`items.py`:

    class NewsItem(scrapy.Item):
        url = scrapy.Field()
        title = scrapy.Field()
        user = scrapy.Field()

Now, you have to create a file called `validators.py` into the project folder
and define the required data model (based on [Schematics](https://github.com/schematics/schematics))
for the items that your spider will collect:

`validators.py`:

    from schematics.models import Model
    from schematics.types import URLType, StringType


    class NewsItem(Model):
        url = URLType(required=True)
        title = StringType(required=True, max_length=200)
        user = StringType(required=True, max_length=50)

After that, you need to enable the `ItemValidationPipeline`, set the validation model for your items and tell the pipeline to drop items that don't match the model:

`settings.py`:

    ITEM_PIPELINES = {
        'spidermon.contrib.scrapy.pipelines.ItemValidationPipeline': 800,
    }
    SPIDERMON_VALIDATION_MODELS = (
        'reddit_spidermon_demo.validators.NewsItem',
    )
    SPIDERMON_VALIDATION_DROP_ITEMS_WITH_ERRORS = True

If spider generates few different types of item it's possible to define validation models per every item.
The same is applicable for `SPIDERMON_VALIDATION_SCHEMAS`.
Just define setting as a dict in `settings.py`, where keys are item class objects and validators are values,
one or several of them (list or tuple in that case):

    from reddit_spidermon_demo.items import NewsItem, SomeOtherItem # SomeOtherItem not in the demo

    SPIDERMON_VALIDATION_MODELS = {
        NewsItem: 'reddit_spidermon_demo.validators.NewsItem',
        SomeOtherItem: ['reddit_spidermon_demo.validators.SomeOtherItem', ], # validator not in the demo
    }

Note, that only listed types of items will be processed in that case.

You could also set the pipeline to include the validation error as a field in the item (although it may not be necessary, since the validation errors are included in the crawling stats and your monitor can check them once the spiders finishes):

    SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS = True

By default, it adds a field called `_validation` to the item when the item doesn't match the schema:

    {
        'title': u'Nchan: HTTP pub/sub server on top of nginx (via long-polling, SSE, etc)',
        'url': u'https://nchan.slact.net/',
        'user': u'liotier',
        '_validation': defaultdict(<type 'list'>, {'title': ['Field too long']})
    }
