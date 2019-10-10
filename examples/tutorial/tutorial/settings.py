# -*- coding: utf-8 -*-
BOT_NAME = "tutorial"

SPIDER_MODULES = ["tutorial.spiders"]
NEWSPIDER_MODULE = "tutorial.spiders"
ROBOTSTXT_OBEY = True

SPIDERMON_ENABLED = True

EXTENSIONS = {"spidermon.contrib.scrapy.extensions.Spidermon": 500}

SPIDERMON_SPIDER_CLOSE_MONITORS = ("tutorial.monitors.SpiderCloseMonitorSuite",)

SPIDERMON_TELEGRAM_SENDER_TOKEN = ""
SPIDERMON_TELEGRAM_RECIPIENTS = [""]

ITEM_PIPELINES = {"spidermon.contrib.scrapy.pipelines.ItemValidationPipeline": 800}
SPIDERMON_VALIDATION_MODELS = ("tutorial.validators.QuoteItem",)

SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS = True

STATS_CLASS = (
    "spidermon.contrib.stats.statscollectors.LocalStorageStatsHistoryCollector"
)

SPIDERMON_MAX_STORED_STATS = 10  # Stores the stats of the last 10 spider execution

SPIDERMON_PERIODIC_MONITORS = {
    "tutorial.monitors.PeriodicMonitorSuite": 10  # every 10 seconds
}
