

import pytest
from scrapy import Field, Item, signals
from scrapy.spiders import Spider
from scrapy.utils.test import get_crawler


class TestItem(Item):
    ...


@pytest.fixture
def spider():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_FIELD_COVERAGE": {},
    }
    crawler = get_crawler(settings_dict=settings)

    spider = Spider.from_crawler(crawler, "example.com")

    return spider


def test_add_stats_item_scraped_count_by_item_type(spider):
    for _ in range(15):
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item={"_type": "regular_dict"},
            response="",
            spider=spider,
        )

    for _ in range(20):
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped, item=Item(), response="", spider=spider,
        )

    for _ in range(25):
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped, item=TestItem(), response="", spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count") == 60
    assert stats.get("spidermon_item_scraped_count/dict") == 15
    assert stats.get("spidermon_item_scraped_count/Item") == 20
    assert stats.get("spidermon_item_scraped_count/TestItem") == 25
