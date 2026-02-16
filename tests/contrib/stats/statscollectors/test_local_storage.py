import os
from collections import deque

import pytest

pytest.importorskip("scrapy")

from scrapy import Spider
from scrapy.utils.defer import deferred_f_from_coro_f
from scrapy.utils.project import data_path
from scrapy.utils.test import get_crawler

from spidermon.contrib.stats.statscollectors.local_storage import (
    LocalStorageStatsHistoryCollector,
)


async def stop_crawler(crawler):
    if hasattr(crawler, "stop_async"):
        await crawler.stop_async()
    else:
        await crawler.stop()


@pytest.fixture
def stats_temporary_location(monkeypatch, tmp_path):
    monkeypatch.setattr(
        LocalStorageStatsHistoryCollector,
        "_stats_location",
        lambda x, y: os.path.join(str(tmp_path), "stats"),
    )


@pytest.fixture
def test_settings():
    return {
        "STATS_CLASS": (
            "spidermon.contrib.stats.statscollectors.local_storage.LocalStorageStatsHistoryCollector"
        ),
    }


@deferred_f_from_coro_f
async def test_spider_has_stats_history_attribute_when_opened_with_collector(
    test_settings,
    stats_temporary_location,
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
    stats_temporary_location,
):
    max_stored_stats = 2
    test_settings["SPIDERMON_MAX_STORED_STATS"] = max_stored_stats

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    assert crawler.spider.stats_history == deque()
    assert crawler.spider.stats_history.maxlen == max_stored_stats
    await stop_crawler(crawler)


@pytest.mark.parametrize("initial_max_len,end_max_len", [(5, 2), (5, 10), (5, 5)])
@deferred_f_from_coro_f
async def test_spider_update_stats_history_queue_max_size(
    test_settings,
    stats_temporary_location,
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
    stats_temporary_location,
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
    stats_temporary_location,
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
async def test_spider_limit_number_of_stored_stats(
    test_settings,
    stats_temporary_location,
):
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


def test_able_to_import_deprecated_local_storage_stats_collector_module():
    """
    To avoid an error when importing this stats collector with the old location
    in legacy code, we need to ensure that LocalStorageStatsHistoryCollector can
    be imported as the old module.

    Original module:
    spidermon.contrib.stats.statscollectors.LocalStorageStatsHistoryCollector

    New module:
    spidermon.contrib.stats.statscollectors.local_storage.LocalStorageStatsHistoryCollector
    """
    try:
        from spidermon.contrib.stats.statscollectors import (
            LocalStorageStatsHistoryCollector,  # noqa: F401
        )
    except ModuleNotFoundError:
        assert False, (
            "Unable to import spidermon.contrib.stats.statscollectors.LocalStorageStatsHistoryCollector"
        )


@deferred_f_from_coro_f
async def test_stats_location_env_spider_name(test_settings):
    statsdir = data_path("stats", createdir=False)
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")

    os.environ["SHUB_VIRTUAL_SPIDER"] = "virtual_spider"

    actual = crawler.stats._stats_location(crawler.spider)
    expected = os.path.join(statsdir, "virtual_spider_stats_history")
    assert actual == expected
    await stop_crawler(crawler)
    del os.environ["SHUB_VIRTUAL_SPIDER"]


@deferred_f_from_coro_f
async def test_stats_location_regular_spider_name(test_settings):
    statsdir = data_path("stats", createdir=False)
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")

    actual = crawler.stats._stats_location(crawler.spider)
    expected = os.path.join(statsdir, "foo_spider_stats_history")
    assert actual == expected
    await stop_crawler(crawler)
