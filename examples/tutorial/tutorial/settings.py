# -*- coding: utf-8 -*-
BOT_NAME = "tutorial"

SPIDER_MODULES = ["tutorial.spiders"]
NEWSPIDER_MODULE = "tutorial.spiders"
ROBOTSTXT_OBEY = True

SPIDERMON_ENABLED = True

EXTENSIONS = {"spidermon.contrib.scrapy.extensions.Spidermon": 500}

SPIDERMON_SPIDER_CLOSE_MONITORS = ("tutorial.monitors.SpiderCloseMonitorSuite",)

SPIDERMON_SLACK_FAKE = True

SPIDERMON_SLACK_SENDER_TOKEN = "your_sender_token"
SPIDERMON_SLACK_SENDER_NAME = "your_sender_name"
SPIDERMON_SLACK_RECIPIENTS = ["@yourself", "#yourprojectchannel"]

ITEM_PIPELINES = {"spidermon.contrib.scrapy.pipelines.ItemValidationPipeline": 800}
SPIDERMON_VALIDATION_MODELS = ("tutorial.validators.QuoteItem",)

SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS = True

SPIDERMON_PERIODIC_MONITORS = {
    "tutorial.monitors.PeriodicMonitorSuite": 10  # every 10 seconds
}
