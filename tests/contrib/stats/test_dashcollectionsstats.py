from collections import deque

import pytest

from scrapy import Spider
from scrapy.utils.test import get_crawler
from spidermon.contrib.stats.statscollectors import DashCollectionsStatsHistoryCollector


class StoreMock:
    stored_data = []

    def iter(self):
        yield from self.stored_data
        self.stored_data = []

    def set(self, data):
        self.stored_data.append(data)

@pytest.fixture
def stats_collection(monkeypatch):
    store = StoreMock()
    monkeypatch.setattr(
        DashCollectionsStatsHistoryCollector,
        "_open_collection",
        lambda *args: store,
    )

@pytest.fixture
def test_settings():
    return {
        "STATS_CLASS": (
            "spidermon.contrib.stats.statscollectors.DashCollectionsStatsHistoryCollector"
        )
    }


def test_spider_has_stats_history_attribute_when_opened_with_collector(
    test_settings, stats_collection
):
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("garbage", "value")
    assert hasattr(crawler.spider, "stats_history")
    assert crawler.spider.stats_history == deque()
    crawler.stop()


def test_spider_has_stats_history_queue_with_specified_max_size(
    test_settings, stats_collection
):
    max_stored_stats = 2
    test_settings["SPIDERMON_MAX_STORED_STATS"] = max_stored_stats

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    assert crawler.spider.stats_history == deque()
    assert crawler.spider.stats_history.maxlen == max_stored_stats
    crawler.stop()

@pytest.mark.parametrize("initial_max_len,end_max_len", [(5, 2), (5, 10), (5, 5)])
def test_spider_update_stats_history_queue_max_size(
    test_settings, stats_collection, initial_max_len, end_max_len
):
    test_settings["SPIDERMON_MAX_STORED_STATS"] = initial_max_len
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    assert crawler.spider.stats_history.maxlen == initial_max_len
    crawler.stop()

    test_settings["SPIDERMON_MAX_STORED_STATS"] = end_max_len
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    assert crawler.spider.stats_history.maxlen == end_max_len
    crawler.stop()


def test_spider_has_last_stats_history_when_opened_again(
    test_settings, stats_collection
):
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("first_execution", "value")
    crawler.stop()

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    assert len(crawler.spider.stats_history) == 1
    assert crawler.spider.stats_history[0]["first_execution"] == "value"
    crawler.stop()

def test_spider_has_two_last_stats_history_when_opened_third_time(
    test_settings, stats_collection
):
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("first_execution", "value")
    crawler.stop()

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("second_execution", "value")
    crawler.stop()

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    assert len(crawler.spider.stats_history) == 2
    assert "second_execution" in crawler.spider.stats_history[0].keys()
    assert "first_execution" in crawler.spider.stats_history[1].keys()
    crawler.stop()

def test_spider_limit_number_of_stored_stats(test_settings, stats_collection):
    test_settings["SPIDERMON_MAX_STORED_STATS"] = 2
    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("first_execution", "value")
    crawler.stop()

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("second_execution", "value")
    crawler.stop()

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    crawler.stats.set_value("third_execution", "value")
    crawler.stop()

    crawler = get_crawler(Spider, test_settings)
    crawler.crawl("foo_spider")
    assert len(crawler.spider.stats_history) == 2
    assert "third_execution" in crawler.spider.stats_history[0].keys()
    assert "second_execution" in crawler.spider.stats_history[1].keys()
    crawler.stop()
