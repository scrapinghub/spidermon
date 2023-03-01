from spidermon.contrib.scrapy.runners import SpiderMonitorResult
from scrapy import Spider
from scrapy.crawler import Crawler
import logging

LOGGER = logging.getLogger(__name__)


def get_spider(settings):
    crawler = Crawler(Spider, settings=settings)
    return Spider.from_crawler(crawler, name="dummy")


def test_declare_settings_false(caplog):
    settings = {
        "SPIDERMON_DUMMY_SETTING": "DUMMY VALUE",
        "SPIDERMON_LOG_SETTINGS": False,
    }

    spider = get_spider(settings)
    suite = SpiderMonitorResult(spider)
    with caplog.at_level(logging.INFO):
        suite.declare_settings()

    assert "SPIDERMON_LOG_SETTINGS: False" in caplog.text
    assert "SPIDERMON_DUMMY_SETTING: DUMMY VALUE" not in caplog.text


def test_declare_settings_true(caplog):
    settings = {
        "SPIDERMON_DUMMY_SETTING": "DUMMY VALUE",
        "SPIDERMON_LOG_SETTINGS": True,
    }

    spider = get_spider(settings)
    suite = SpiderMonitorResult(spider)
    with caplog.at_level(logging.INFO):
        suite.declare_settings()

    assert "SPIDERMON_LOG_SETTINGS: True" in caplog.text
    assert "SPIDERMON_DUMMY_SETTING: DUMMY VALUE" in caplog.text
