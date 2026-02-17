import pytest

pytest.importorskip("scrapy")

from collections import deque
from typing import Any
from unittest.mock import MagicMock, patch

import scrapinghub
from packaging.version import Version
from scrapy import Spider
from scrapy.utils.defer import deferred_f_from_coro_f
from scrapy.utils.test import get_crawler

from spidermon.contrib.stats.statscollectors.sc_collections import (
    ScrapyCloudCollectionsStatsHistoryCollector,
)
from tests import SCRAPY_VERSION


async def stop_crawler(crawler):
    if hasattr(crawler, "stop_async"):
        await crawler.stop_async()
    else:
        await crawler.stop()


class StoreMock:
    stored_data: list[Any] = []
    raise_iter_error = False

    def iter(self):
        if self.raise_iter_error:
            raise scrapinghub.client.exceptions.NotFound
        yield from self.stored_data
        self.stored_data = []

    def set(self, data):
        self.stored_data.append(data)


@pytest.fixture
def stats_collection(monkeypatch):
    store = StoreMock()
    monkeypatch.setattr(
        ScrapyCloudCollectionsStatsHistoryCollector,
        "_open_collection",
        lambda *args: store,
    )


@pytest.fixture
def stats_collection_not_exist(monkeypatch):
    store = StoreMock()
    store.raise_iter_error = True
    monkeypatch.setattr(
        ScrapyCloudCollectionsStatsHistoryCollector,
        "_open_collection",
        lambda *args: store,
    )


@pytest.fixture
def test_settings():
    return {
        "STATS_CLASS": (
            "spidermon.contrib.stats.statscollectors.sc_collections.ScrapyCloudCollectionsStatsHistoryCollector"
        ),
    }


@patch("spidermon.contrib.stats.statscollectors.sc_collections.scrapinghub")
def test_open_spider_without_api(scrapinghub_mock, test_settings):
    crawler = get_crawler(Spider, test_settings)
    pipe = ScrapyCloudCollectionsStatsHistoryCollector(crawler)

    args = [MagicMock()] if Version("2.14") > SCRAPY_VERSION else []
    pipe.open_spider(*args)

    assert pipe.store is None


@patch("spidermon.contrib.stats.statscollectors.sc_collections.scrapinghub")
@patch("spidermon.contrib.stats.statscollectors.sc_collections.os.environ.get")
def test_open_collection_with_api(scrapinghub_mock, os_environ_mock, test_settings):
    mock_spider = MagicMock()
    mock_spider.name = "test"

    os_environ_mock.return_value = 1234
    crawler = get_crawler(Spider, test_settings)
    pipe = ScrapyCloudCollectionsStatsHistoryCollector(crawler)

    store = pipe._open_collection(mock_spider)

    assert store is not None


@deferred_f_from_coro_f
async def test_spider_has_stats_history_attribute_when_opened_with_collector(
    test_settings,
    stats_collection,
):
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("garbage", "value")
    assert hasattr(crawler.spider, "stats_history")
    assert crawler.spider.stats_history == deque()
    await stop_crawler(crawler)


@deferred_f_from_coro_f
async def test_spider_has_stats_history_queue_with_specified_max_size(
    test_settings,
    stats_collection,
):
    max_stored_stats = 2
    test_settings["SPIDERMON_MAX_STORED_STATS"] = max_stored_stats

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    assert crawler.spider.stats_history == deque()
    assert crawler.spider.stats_history.maxlen == max_stored_stats
    await stop_crawler(crawler)


@pytest.mark.parametrize(("initial_max_len", "end_max_len"), [(5, 2), (5, 10), (5, 5)])
@deferred_f_from_coro_f
async def test_spider_update_stats_history_queue_max_size(
    test_settings,
    stats_collection,
    initial_max_len,
    end_max_len,
):
    test_settings["SPIDERMON_MAX_STORED_STATS"] = initial_max_len
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    assert crawler.spider.stats_history.maxlen == initial_max_len
    await stop_crawler(crawler)

    test_settings["SPIDERMON_MAX_STORED_STATS"] = end_max_len
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    assert crawler.spider.stats_history.maxlen == end_max_len
    await stop_crawler(crawler)


@deferred_f_from_coro_f
async def test_spider_has_last_stats_history_when_opened_again(
    test_settings,
    stats_collection,
):
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("first_execution", "value")
    await stop_crawler(crawler)

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    assert len(crawler.spider.stats_history) == 1
    assert crawler.spider.stats_history[0]["first_execution"] == "value"
    await stop_crawler(crawler)


@deferred_f_from_coro_f
async def test_spider_has_two_last_stats_history_when_opened_third_time(
    test_settings,
    stats_collection,
):
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("first_execution", "value")
    await stop_crawler(crawler)

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("second_execution", "value")
    await stop_crawler(crawler)

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    assert len(crawler.spider.stats_history) == 2
    assert "second_execution" in crawler.spider.stats_history[0].keys()
    assert "first_execution" in crawler.spider.stats_history[1].keys()
    await stop_crawler(crawler)


@deferred_f_from_coro_f
async def test_spider_limit_number_of_stored_stats(test_settings, stats_collection):
    test_settings["SPIDERMON_MAX_STORED_STATS"] = 2
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("first_execution", "value")
    await stop_crawler(crawler)

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("second_execution", "value")
    await stop_crawler(crawler)

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("third_execution", "value")
    await stop_crawler(crawler)

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    assert len(crawler.spider.stats_history) == 2
    assert "third_execution" in crawler.spider.stats_history[0].keys()
    assert "second_execution" in crawler.spider.stats_history[1].keys()
    await stop_crawler(crawler)


@deferred_f_from_coro_f
@patch("spidermon.contrib.stats.statscollectors.sc_collections.os.environ.get")
async def test_job_id_added(mock_os_enviorn_get, test_settings, stats_collection):
    mock_os_enviorn_get.return_value = "test/test/test"
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    await stop_crawler(crawler)

    mock_os_enviorn_get.assert_called_with("SCRAPY_JOB", "")
    assert (
        crawler.spider.stats_history[0]["job_url"]
        == "https://app.zyte.com/p/test/test/test"
    )


@deferred_f_from_coro_f
@patch("spidermon.contrib.stats.statscollectors.sc_collections.os.environ.get")
async def test_job_id_not_available(
    mock_os_enviorn_get,
    test_settings,
    stats_collection,
):
    mock_os_enviorn_get.return_value = None
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    await stop_crawler(crawler)

    mock_os_enviorn_get.assert_called_with("SCRAPY_JOB", "")
    assert "job_url" not in crawler.spider.stats_history[0]


@patch("spidermon.contrib.stats.statscollectors.sc_collections.os.environ.get")
def test_stats_history_when_no_collection(
    os_enviorn_mock,
    stats_collection_not_exist,
    test_settings,
):
    mock_spider = MagicMock()
    mock_spider.crawler.settings.getint.return_value = 100
    mock_spider.name = "test"

    os_enviorn_mock.return_value = 1234
    crawler = get_crawler(Spider, test_settings)
    crawler.spider = mock_spider
    pipe = ScrapyCloudCollectionsStatsHistoryCollector(crawler)
    args = [mock_spider] if Version("2.14") > SCRAPY_VERSION else []
    pipe.open_spider(*args)
    assert mock_spider.stats_history == deque(maxlen=100)
