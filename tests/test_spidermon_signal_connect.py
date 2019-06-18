import sys

import pytest
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.spiders import Spider

from spidermon.contrib.scrapy.extensions import Spidermon


def get_crawler(settings_dict=None):
    runner = CrawlerRunner(settings_dict)
    return runner.create_crawler(Spider)


@pytest.mark.skipif(sys.version_info < (3, 4), reason="requires python3.4 or higher")
def test_spider_opened_connect_signal(mocker):
    spider_opened_method = mocker.patch.object(Spidermon, "spider_opened")

    crawler = get_crawler(
        settings_dict={
            "SPIDERMON_ENABLED": True,
            "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        }
    )
    spider = Spider.from_crawler(crawler, "example.com")
    crawler.signals.send_catch_log(signal=signals.spider_opened, spider=spider)

    assert spider_opened_method.called, "spider_opened not called"


@pytest.mark.skipif(sys.version_info < (3, 4), reason="requires python3.4 or higher")
def test_spider_closed_connect_signal(mocker):
    spider_closed_method = mocker.patch.object(Spidermon, "spider_closed")

    crawler = get_crawler(
        settings_dict={
            "SPIDERMON_ENABLED": True,
            "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        }
    )
    spider = Spider.from_crawler(crawler, "example.com")
    crawler.signals.send_catch_log(
        signal=signals.spider_closed, spider=spider, reason=None
    )

    assert spider_closed_method.called, "spider_closed not called"


@pytest.mark.skipif(sys.version_info < (3, 4), reason="requires python3.4 or higher")
def test_engine_stopped_connect_signal(mocker):
    engine_stopped = mocker.patch.object(Spidermon, "engine_stopped")

    crawler = get_crawler(
        settings_dict={
            "SPIDERMON_ENABLED": True,
            "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        }
    )
    spider = Spider.from_crawler(crawler, "example.com")
    crawler.signals.send_catch_log(
        signal=signals.engine_stopped, spider=spider, reason=None
    )

    assert engine_stopped.called, "engine_stopped not called"
