import sys

import pytest
from scrapy import signals
from scrapy.spiders import Spider
from scrapy.utils.test import get_crawler

from spidermon.contrib.scrapy.extensions import Spidermon


@pytest.fixture
def spidermon_enabled_settings():
    return {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
    }


def test_spider_opened_connect_signal(mocker, spidermon_enabled_settings):
    spider_opened_method = mocker.patch.object(Spidermon, "spider_opened")

    crawler = get_crawler(settings_dict=spidermon_enabled_settings)
    spider = Spider.from_crawler(crawler, "example.com")
    crawler.signals.send_catch_log(signal=signals.spider_opened, spider=spider)

    assert spider_opened_method.called, "spider_opened not called"


def test_spider_closed_connect_signal(mocker, spidermon_enabled_settings):
    spider_closed_method = mocker.patch.object(Spidermon, "spider_closed")

    crawler = get_crawler(settings_dict=spidermon_enabled_settings)
    spider = Spider.from_crawler(crawler, "example.com")
    crawler.signals.send_catch_log(
        signal=signals.spider_closed, spider=spider, reason=None
    )

    assert spider_closed_method.called, "spider_closed not called"


def test_engine_stopped_connect_signal(mocker, spidermon_enabled_settings):
    engine_stopped = mocker.patch.object(Spidermon, "engine_stopped")

    crawler = get_crawler(settings_dict=spidermon_enabled_settings)
    spider = Spider.from_crawler(crawler, "example.com")
    crawler.signals.send_catch_log(
        signal=signals.engine_stopped, spider=spider, reason=None
    )

    assert engine_stopped.called, "engine_stopped not called"


def test_item_scraped_connect_signal_if_field_coverage_settings_enabled(
    mocker, spidermon_enabled_settings
):
    item_scraped_method = mocker.patch.object(Spidermon, "item_scraped")

    spidermon_enabled_settings["SPIDERMON_ADD_FIELD_COVERAGE"] = True
    crawler = get_crawler(settings_dict=spidermon_enabled_settings)

    spider = Spider.from_crawler(crawler, "example.com")
    crawler.signals.send_catch_log(signal=signals.item_scraped, spider=spider)

    assert item_scraped_method.called, "item_scraped_method not called"


def test_item_scraped_do_not_connect_signal_if_field_coverage_settings_disabled(
    mocker, spidermon_enabled_settings
):
    item_scraped_method = mocker.patch.object(Spidermon, "item_scraped")

    spidermon_enabled_settings["SPIDERMON_ADD_FIELD_COVERAGE"] = False

    crawler = get_crawler(settings_dict=spidermon_enabled_settings)

    spider = Spider.from_crawler(crawler, "example.com")
    crawler.signals.send_catch_log(signal=signals.item_scraped, spider=spider)

    assert not item_scraped_method.called, "item_scraped_method called"


def test_item_scraped_do_not_connect_signal_if_do_not_have_field_coverage_settings(
    mocker, spidermon_enabled_settings
):
    item_scraped_method = mocker.patch.object(Spidermon, "item_scraped")

    crawler = get_crawler(settings_dict=spidermon_enabled_settings)

    spider = Spider.from_crawler(crawler, "example.com")
    crawler.signals.send_catch_log(signal=signals.item_scraped, spider=spider)

    assert not item_scraped_method.called, "item_scraped_method called"
