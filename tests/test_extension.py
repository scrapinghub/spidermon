try:
    import unittest.mock as mock
except ImportError:
    import mock
import pytest

from scrapy import signals
from spidermon.contrib.scrapy.extensions import Spidermon


@pytest.fixture
def suites():
    return ["tests.fixtures.suites.Suite01"]


def test_spider_opened_suites_should_run(get_crawler, suites):
    """The suites defined at spider_opened_suites should be loaded and run """
    crawler = get_crawler()
    spidermon = Spidermon(crawler, spider_opened_suites=suites)
    spidermon.spider_opened_suites[0].run = mock.MagicMock()
    spidermon.spider_opened(crawler.spider)
    assert spidermon.spider_opened_suites[0].__class__.__name__ == "Suite01"
    spidermon.spider_opened_suites[0].run.assert_called_once_with(mock.ANY)


def test_spider_closed_suites_should_run(get_crawler, suites):
    """The suites defined at spider_closed_suites should be loaded and run """
    crawler = get_crawler()
    spidermon = Spidermon(
        crawler, spider_opened_suites=suites, spider_closed_suites=suites
    )
    spidermon.spider_closed_suites[0].run = mock.MagicMock()
    spidermon.spider_opened(crawler.spider)
    spidermon.spider_closed(crawler.spider)
    assert spidermon.spider_closed_suites[0].__class__.__name__ == "Suite01"
    spidermon.spider_closed_suites[0].run.assert_called_once_with(mock.ANY)


def test_engine_stopped_suites_should_run(get_crawler, suites):
    """The suites defined at engine_stopped_suites should be loaded and run """
    crawler = get_crawler()
    spidermon = Spidermon(crawler, engine_stopped_suites=suites)
    spidermon.engine_stopped_suites[0].run = mock.MagicMock()
    spidermon.engine_stopped()
    assert spidermon.engine_stopped_suites[0].__class__.__name__ == "Suite01"
    spidermon.engine_stopped_suites[0].run.assert_called_once_with(mock.ANY)


def test_spider_opened_suites_should_run_from_signal(get_crawler, suites):
    """The suites defined at SPIDERMON_SPIDER_OPEN_MONITORS setting should be loaded and run """
    settings = {"SPIDERMON_SPIDER_OPEN_MONITORS": suites}
    crawler = get_crawler(settings)
    spidermon = Spidermon.from_crawler(crawler)
    spidermon.spider_opened_suites[0].run = mock.MagicMock()
    crawler.signals.send_catch_log(signal=signals.spider_opened, spider=crawler.spider)
    spidermon.spider_opened_suites[0].run.assert_called_once_with(mock.ANY)


def test_spider_closed_suites_should_run_from_signal(get_crawler, suites):
    """The suites defined at SPIDERMON_SPIDER_CLOSE_MONITORS setting should be loaded and run """
    settings = {"SPIDERMON_SPIDER_CLOSE_MONITORS": suites}
    crawler = get_crawler(settings)
    spidermon = Spidermon.from_crawler(crawler)
    spidermon.spider_closed_suites[0].run = mock.MagicMock()
    crawler.signals.send_catch_log(signal=signals.spider_closed, spider=crawler.spider)
    spidermon.spider_closed_suites[0].run.assert_called_once_with(mock.ANY)


def test_engine_stopped_suites_should_run_from_signal(get_crawler, suites):
    """The suites defined at SPIDERMON_ENGINE_STOP_MONITORS setting should be loaded and run """
    settings = {"SPIDERMON_ENGINE_STOP_MONITORS": suites}
    crawler = get_crawler(settings)
    spidermon = Spidermon.from_crawler(crawler)
    spidermon.engine_stopped_suites[0].run = mock.MagicMock()
    crawler.signals.send_catch_log(signal=signals.engine_stopped, spider=crawler.spider)
    spidermon.engine_stopped_suites[0].run.assert_called_once_with(mock.ANY)
