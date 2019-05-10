from spidermon.contrib.stats.statscollectors import LocalStorageStatsHistoryCollector
from collections import deque


def test_spider_has_stats_history_attribute_when_opened_with_collector(get_crawler):
    crawler = get_crawler()
    spider = crawler._create_spider("foo")
    assert not hasattr(spider, "stats_history")

    stats_collector = LocalStorageStatsHistoryCollector(crawler)
    stats_collector.open_spider(spider)

    assert hasattr(spider, "stats_history")
    assert spider.stats_history == deque()
