Getting started with Spidermon
============================

Spidermon is a tool that lets you monitor your spiders. In this tutorial you will learn how to set up Spidermon to monitor a simple spider, checking if the execution has extracted the expected amount of items, and sending back to you a Slack message with the status of the execution.

To do that, we will work in a very simple project, with a single spider that collects data from [http://reddit.com/r/programming](http://reddit.com/r/programming) posts. But you can use whichever project you want.

The code for our project is available at: [http://github.com/stummjr/spidermon-reddit-example](http://github.com/stummjr/spidermon-reddit-example). You can have an overview in the most important parts here:

`spiders/reddit.py`:

    # -*- coding: utf-8 -*-
    import scrapy
    from reddit_spidermon_demo.items import NewsItem


    class RedditSpider(scrapy.Spider):
        name = "reddit"
        allowed_domains = ["reddit.com"]
        start_urls = (
            'http://www.reddit.com/r/programming',
        )

        def parse(self, response):
            for submission_sel in response.css("div.entry"):
                item = NewsItem()
                item['url'] = submission_sel.css("a.title ::attr(href)").extract_first()
                item['title'] = submission_sel.css("a.title ::text").extract_first()
                item['user'] = submission_sel.css("a.author ::text").extract_first()
                yield item


`items.py`:

    import scrapy

    class NewsItem(scrapy.Item):
        url = scrapy.Field()
        title = scrapy.Field()
        user = scrapy.Field()

## How Spidermon works?
Spidermon is an extension to Scrapy that lets you write monitors for your Scrapy
crawlers. To use it, you need to define specific **monitors** and **validators** for your use cases.

- **Monitor**: a monitor is like a test case that will be executed when your spider starts or finishes its execution.
- **Validator**: a validator defines the schema (data model) that an item must comply with. It will be used by the `ItemValidationPipeline`, that will check if every item matches the given schema.

In a high level, the **workflow of Spidermon** will be something like this:

1. You start your spider and, if configured to, Spidermon runs the tests defined in your **open monitors** and/or send notifications about the upcoming execution.
2. `ItemValidationPipeline` checks if the schema of each item matches the one defined in your `validators.py` file.
3. When your spider finishes, Spidermon runs the tests from your **close monitors**.
4. Spidermon build a report and send it through email, slack or it stores the report in a S3 bucket.

This way, you leave the monitoring task to Spidermon and just check the reports/notifications.


## Install Spidermon and dependencies
Spidermon:
**TODO**: install with pip

    git clone "git@github.com:scrapinghub/spidermon.git"
    cd spidermon && pip install .

Dependencies:

    pip install schematics python-slugify jinja2 premailer boto slackclient jsonschema


## Using Spidermon in your project
_(clone the [base project of our example], or use your own project to follow this)_

Now that everything is installed, you must define a validator for the items that your spider collects and set up a monitor for our crawler and notifications.


### Set up the Validators
Start by creating a file called `validators.py` in your project and defining the data model for the items inside it:

`validators.py`

    from schematics.models import Model
    from schematics.types import URLType, StringType


    class NewsItem(Model):
        url = URLType(required=True)
        title = StringType(required=True, max_length=200)
        user = StringType(required=True, max_length=50)


After that, you need to enable the `ItemValidationPipeline` and set the validation models for your items in the `settings.py` file:

    ITEM_PIPELINES = {
        'spidermon.contrib.scrapy.pipelines.ItemValidationPipeline': 800,
    }

    SPIDERMON_VALIDATION_MODELS = (
        'reddit_spidermon_demo.validators.NewsItem',
    )

Now, when you run your crawler, each item will be checked against the `NewsItem` model.

You can configure the pipeline to drop items that do not match the model:

    SPIDERMON_VALIDATION_DROP_ITEMS_WITH_ERRORS = True

Or to include the validation error as a field in the item:

    SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS = True

By default, it adds a field called `_validation` to the item, but the field name can be configured through this setting:

    SPIDERMON_VALIDATION_ERRORS_FIELD = 'validation_error'

This is how an item would look like if it doesn't match the expected schema:

    {
        'title': u'Nchan: HTTP pub/sub server on top of nginx (via long-polling, SSE, etc)',
        'url': u'https://nchan.slact.net/',
        'user': u'liotier',
        'validation_error': defaultdict(<type 'list'>, {'title': ['Field too long']})
    }


### Set up the Monitors
The monitors are like test cases that will be executed to check the status of your crawling and the items collected. Let's define a monitor that ensures that each crawl gets exactly 25 items, that is the default amount of items from each reddit page.

Before coding the monitor, you need to enable the Spidermon extension in `settings.py`:

    EXTENSIONS = {
        'spidermon.contrib.scrapy.extensions.Spidermon': 500,
    }


And also set the monitors that will be called when the spider is opened:

    SPIDERMON_SPIDER_OPEN_MONITORS = (
        'reddit_spidermon_demo.monitors.SpiderOpenMonitorSuite',
    )

And closed:

    SPIDERMON_SPIDER_CLOSE_MONITORS = (
        'reddit_spidermon_demo.monitors.SpiderCloseMonitorSuite',
    )

Now, you have to create the `SpiderOpenMonitorSuite` and `SpiderCloseMonitorSuite` classes in a file called `monitors.py`:

    from spidermon import MonitorSuite    
    from spidermon.contrib.actions.slack.notifiers import (
        SendSlackMessageSpiderStarted, SendSlackMessageSpiderFinished
    )

    class SpiderOpenMonitorSuite(MonitorSuite):
        monitors_finished_actions = [
            SendSlackMessageSpiderStarted,
        ]

    class SpiderCloseMonitorSuite(MonitorSuite):
        monitors = [
            ItemCountMonitor,
        ]
        monitors_finished_actions = [
            SendSlackMessageSpiderFinished,
        ]

Each `MonitorSuite` is configured through lists of monitors and actions. In the example above, Spidermon will send a notification through Slack, when a spider starts and finishes its job.

Spidermon will also run `ItemCountMonitor`, which should be defined in the same file. That monitor is reponsible for checking whether the spider generated the expected amount of items or not:


    from spidermon import Monitor, monitors
    from spidermon.contrib.monitors.mixins import StatsMonitorMixin, JobMonitorMixin

    \@monitors.name('Item count')
    class ItemCountMonitor(Monitor, StatsMonitorMixin, JobMonitorMixin):
        \@monitors.name('Minimum number of items')
        def test_minimum_number_of_items(self):
            minimum = 25
            msg = 'Number of scraped items is less than %d' % minimum
            self.assertGreaterEqual(self.item_scraped_count(), minimum, msg=msg)

        def item_scraped_count(self):
            return getattr(self.stats, 'item_scraped_count', 0)


Spidermon includes the results of the tests it runs in the notification that you will get in Slack.


### Set up the notifications
To get Spidermon sending messages to Slack, you need to set it up in `settings.py`:

    # Slack
    SPIDERMON_SLACK_SENDER_TOKEN = '<SLACK_API_TOKEN>'
    SPIDERMON_SLACK_SENDER_NAME = 'bender'
    SPIDERMON_SLACK_RECIPIENTS = ['@yourself', '@yourteammate']
    SPIDERMON_SLACK_FAKE = False

That's it. Now, run your crawler and wait for the Slack notification.


### More information
This is just a basic tutorial. Spidermon is much more powerful. You can setup templates for detailed reports, set Spidermon to send it by email, among other features.
