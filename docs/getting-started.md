Getting started with Spidermon
==============================

Spidermon is a monitoring tool for Scrapy spiders. Spidermon allows you to write monitors to notify you about the execution of your spiders.

This tutorial shows how to set up Spidermon to monitor a spider, checking if the execution has extracted the expected amount of items, and sending back to you a Slack message with the status of the execution.

You can use [a simple project](http://github.com/stummjr/spidermon-reddit-example) that we built to follow this tutorial. Clone it and follow the steps presented here.


## Install Spidermon and dependencies

    git clone "git@github.com:scrapinghub/spidermon.git"
    cd spidermon && pip install . -r requirements.txt -r requirements/validation.txt


## Using Spidermon in your project
Now that everything is installed, you must define a validator for the items that your spider collects, set up a monitor for your crawler and configure the slack notifications that Spidermon will send to you.


### Set up the Validators
The validators define the expected structure for the items. As you can see in the [code for this tutorial](http://github.com/stummjr/spidermon-reddit-example), the `reddit` spider generates `NewsItem` objects with the scraped data:

`items.py`:

    class NewsItem(scrapy.Item):
        url = scrapy.Field()
        title = scrapy.Field()
        user = scrapy.Field()

Now, you have to create a file called `validators.py` into the project folder and define the required data model for the items that your spider will collect:

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


### Set up the Monitors
The monitors are like test cases that will be executed to check if your crawling went OK. In this case, OK means that the spider extracts exactly 25 items each time it runs (25 is the default amount of items in a reddit page).


#### Create the monitors
The monitors will be placed in a new file called `monitors.py`. At first, you must define the `SpiderOpenMonitorSuite` and `SpiderCloseMonitorSuite` classes. In those classes you configure the actions that Spidermon will execute when your spider is **starting** and when it is **finishing**, respectively:

`monitors.py`:

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

The above example sets Spidermon to send a Slack notification when a spider starts and when it finishes its job. It also sets `ItemCountMonitor` to be executed when the spider is closing down.

`ItemCountMonitor` is like a test case for the crawling status and it must be coded inside the same `monitors.py` file:


    from spidermon import Monitor, monitors
    from spidermon.contrib.monitors.mixins import StatsMonitorMixin, JobMonitorMixin

    @monitors.name('Item count')
    class ItemCountMonitor(Monitor, StatsMonitorMixin, JobMonitorMixin):
        @monitors.name('Minimum number of items')
        def test_minimum_number_of_items(self):
            expected = 25
            msg = 'Number of scraped items is different of %d' % expected
            self.assertEqual(self.item_scraped_count(), expected, msg=msg)

        def item_scraped_count(self):
            return getattr(self.stats, 'item_scraped_count', 0)

The results of the tests defined in the monitors are included in the notifications that Spidermon sends through Slack.

Full source code for `monitors.py`:

    from spidermon import Monitor, MonitorSuite, monitors
    from spidermon.contrib.monitors.mixins import StatsMonitorMixin, JobMonitorMixin
    from spidermon.contrib.actions.slack.notifiers import (
        SendSlackMessageSpiderStarted, SendSlackMessageSpiderFinished
    )


    @monitors.name('Item count')
    class ItemCountMonitor(Monitor, StatsMonitorMixin, JobMonitorMixin):
        @monitors.name('Minimum number of items')
        def test_minimum_number_of_items(self):
            expected = 25
            msg = 'Number of scraped items is different of %d' % expected
            self.assertEqual(self.item_scraped_count(), expected, msg=msg)

        def item_scraped_count(self):
            return getattr(self.stats, 'item_scraped_count', 0)


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



#### Enable the monitors
After coding the monitor, you need to enable the Spidermon extension in `settings.py`:

    EXTENSIONS = {
        'spidermon.contrib.scrapy.extensions.Spidermon': 500,
    }


And also set the monitor suite that will be executed when the spider is opened (the **open monitors**):

    SPIDERMON_SPIDER_OPEN_MONITORS = (
        'reddit_spidermon_demo.monitors.SpiderOpenMonitorSuite',
    )

And closed (the **close monitors**):

    SPIDERMON_SPIDER_CLOSE_MONITORS = (
        'reddit_spidermon_demo.monitors.SpiderCloseMonitorSuite',
    )


### Configure Slack notifications
The last step is to configure Spidermon to be able to send the Slack messages that we set up on `monitors.py`. To do that, you have to add these settings to `settings.py`:

    SPIDERMON_SLACK_SENDER_TOKEN = '<SLACK_API_TOKEN>'
    SPIDERMON_SLACK_SENDER_NAME = 'bender'  # our beloved bot :)
    SPIDERMON_SLACK_RECIPIENTS = ['@yourself', '@yourteammate']
    SPIDERMON_SLACK_FAKE = False


That's it. Now, run your crawler and wait for the Slack notification.

You can check the complete source code for this tutorial in the [`spidermon-working`](https://github.com/stummjr/spidermon-reddit-example/tree/spidermon-working) branch in the project repository.


## Wrap up
Spidermon is an extension to Scrapy that lets you write monitors for your Scrapy spiders. As you just seen in this tutorial, you have to define validators and monitors for your project:

- **Validator**: a validator defines the schema (data model) that an item must comply with. It is used by the `ItemValidationPipeline`, that checks if every item matches the given schema.
- **Monitor**: a monitor is like a test case that will be executed when your spider starts or finishes its execution.


At a high level, Spidermon works like this:

1. You start your spider and, if configured to, Spidermon runs the tests defined in your **Open Monitors**. It can also send a notification about the upcoming execution.
2. `ItemValidationPipeline` checks if the schema of each item matches the one defined in your `validators.py` file.
3. When your spider finishes, Spidermon runs the tests from your **Close Monitors**.
4. Spidermon builds a report and sends it through email, Slack or stores it in S3.

This way, you leave the monitoring task to Spidermon and just check the reports/notifications.
