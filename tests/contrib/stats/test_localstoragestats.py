from collections import deque
from spidermon.contrib.stats.statscollectors import LocalStorageStatsHistoryCollector


def test_spider_has_stats_history_attribute_when_opened_with_collector(get_crawler, tmpdir):
    crawler = get_crawler()
    spider = crawler._create_spider("foo")
    assert not hasattr(spider, "stats_history")

    stats_collector = LocalStorageStatsHistoryCollector(crawler)
    stats_collector._statsdir = tmpdir  # TODO use mock here instead of hard-coded assignment

    stats_collector.open_spider(spider)

    assert hasattr(spider, "stats_history")
    assert spider.stats_history == deque()


def test_spider_has_two_last_stats_history_when_opened_third_time(get_crawler, tmpdir):
    crawler = get_crawler()
    spider = crawler._create_spider("foo")

    stats_collector = LocalStorageStatsHistoryCollector(crawler)
    stats_collector._statsdir = tmpdir  # TODO use mock here instead of hard-coded assignment
    stats_collector.open_spider(spider)
    stats_collector.set_value("first_execution", "value")
    stats_collector.close_spider(spider, "finished")

    stats_collector = LocalStorageStatsHistoryCollector(crawler)
    stats_collector._statsdir = tmpdir  # TODO use mock here instead of hard-coded assignment
    stats_collector.open_spider(spider)
    stats_collector.set_value("second_execution", "value")
    stats_collector.close_spider(spider, "finished")

    stats_collector = LocalStorageStatsHistoryCollector(crawler)
    stats_collector._statsdir = tmpdir  # TODO use mock here instead of hard-coded assignment
    stats_collector.open_spider(spider)

    assert len(spider.stats_history) == 2
    assert spider.stats_history[0] == {"second_execution": "value"}
    assert spider.stats_history[1] == {"first_execution": "value"}


def test_spider_has_last_stats_history_when_opened_again(get_crawler, tmpdir):
    crawler = get_crawler()
    spider = crawler._create_spider("foo")

    stats_collector = LocalStorageStatsHistoryCollector(crawler)
    stats_collector._statsdir = tmpdir  # TODO use mock here instead of hard-coded assignment

    stats_collector.open_spider(spider)
    stats_collector.set_value("first_execution", "value")
    stats_collector.close_spider(spider, "finished")

    crawler = get_crawler()
    spider = crawler._create_spider("foo")

    stats_collector = LocalStorageStatsHistoryCollector(crawler)
    stats_collector._statsdir = tmpdir  # TODO use mock here instead of hard-coded assignment

    stats_collector.open_spider(spider)

    assert len(spider.stats_history) == 1
    assert spider.stats_history[0] == {"first_execution": "value"}


def test_spider_limit_number_of_stored_stats(get_crawler, tmpdir):
    crawler = get_crawler({
        "SPIDERMON_MAX_STORED_STATS": 2
    })
    spider = crawler._create_spider("foo")

    stats_collector = LocalStorageStatsHistoryCollector(crawler)
    stats_collector._statsdir = tmpdir  # TODO use mock here instead of hard-coded assignment
    stats_collector.open_spider(spider)
    stats_collector.set_value("first_execution", "value")
    stats_collector.close_spider(spider, "finished")

    stats_collector = LocalStorageStatsHistoryCollector(crawler)
    stats_collector._statsdir = tmpdir  # TODO use mock here instead of hard-coded assignment
    stats_collector.open_spider(spider)
    stats_collector.set_value("second_execution", "value")
    stats_collector.close_spider(spider, "finished")

    stats_collector = LocalStorageStatsHistoryCollector(crawler)
    stats_collector._statsdir = tmpdir  # TODO use mock here instead of hard-coded assignment
    stats_collector.open_spider(spider)
    stats_collector.set_value("third_execution", "value")
    stats_collector.close_spider(spider, "finished")

    stats_collector = LocalStorageStatsHistoryCollector(crawler)
    stats_collector._statsdir = tmpdir  # TODO use mock here instead of hard-coded assignment
    stats_collector.open_spider(spider)

    assert len(spider.stats_history) == 2
    assert spider.stats_history[0] == {"third_execution": "value"}
    assert spider.stats_history[1] == {"second_execution": "value"}
