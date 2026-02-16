import pytest

pytest.importorskip("scrapy")

from scrapy import Item, signals
from scrapy.spiders import Spider
from scrapy.utils.defer import deferred_f_from_coro_f
from scrapy.utils.test import get_crawler


class TestItem(Item):
    __test__ = False


@pytest.fixture
def spider():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
    }
    crawler = get_crawler(settings_dict=settings)

    spider = Spider.from_crawler(crawler, "example.com")

    return spider


async def send_item_scraped(spider, item):
    if hasattr(spider.crawler.signals, "send_catch_log_async"):
        await spider.crawler.signals.send_catch_log_async(
            signal=signals.item_scraped, item=item, response="", spider=spider
        )
    else:
        await spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped, item=item, response="", spider=spider
        )


@deferred_f_from_coro_f
async def test_add_stats_item_scraped_count_by_item_type(spider):
    for _ in range(15):
        await send_item_scraped(spider, {"_type": "regular_dict"})

    for _ in range(20):
        await send_item_scraped(spider, Item())

    for _ in range(25):
        await send_item_scraped(spider, TestItem())

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count") == 60
    assert stats.get("spidermon_item_scraped_count/dict") == 15
    assert stats.get("spidermon_item_scraped_count/Item") == 20
    assert stats.get("spidermon_item_scraped_count/TestItem") == 25


@deferred_f_from_coro_f
async def test_item_scraped_count_single_field(spider):
    returned_items = [{"field1": "value1"}]

    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 1


@deferred_f_from_coro_f
async def test_item_scraped_count_multiple_field(spider):
    returned_items = [{"field1": "value1", "field2": "value2"}]

    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 1
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 1


@deferred_f_from_coro_f
async def test_item_scraped_count_multiple_items(spider):
    returned_items = [
        {"field1": "value1", "field2": "value2"},
        {"field1": "value1", "field2": "value2"},
    ]

    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2


@deferred_f_from_coro_f
async def test_item_scraped_count_multiple_items_field_missing(spider):
    returned_items = [
        {"field1": "value1", "field2": "value2"},
        {
            "field1": "value1",
        },
    ]

    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 1


@deferred_f_from_coro_f
async def test_item_scraped_count_single_nested_field(spider):
    returned_items = [{"field1": {"field1.1": "value1.1"}}]

    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()
    assert stats.get("spidermon_item_scraped_count/dict") == 1
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 1
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.1") == 1


@deferred_f_from_coro_f
async def test_item_scraped_count_multiple_nested_field(spider):
    returned_items = [
        {
            "field1": {"field1.1": "value1.1"},
            "field2": "value2",
            "field3": {"field3.1": "value3.1"},
        },
        {
            "field1": {
                "field1.1": "value1.1",
                "field1.2": "value1.2",
            },
            "field2": "value2",
        },
    ]

    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.2") == 1
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field3") == 1


@deferred_f_from_coro_f
async def test_item_scraped_count_with_slash_on_field_name(spider):
    returned_items = [{"field1/with/slash": "value1", "field2": "value2"}]

    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()
    assert stats.get("spidermon_item_scraped_count/dict/field1/with/slash") == 1
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 1


@deferred_f_from_coro_f
async def test_do_not_add_field_coverage_when_spider_closes_if_do_not_have_field_coverage_settings():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": False,
    }
    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    item = {"field1": "value1"}
    await send_item_scraped(
        spider, item
    )  # Return item to have some stats to calculate coverage

    crawler.signals.send_catch_log(
        signal=signals.spider_closed, spider=spider, reason=None
    )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_field_coverage/dict/field1") is None


@deferred_f_from_coro_f
async def test_add_field_coverage_when_spider_closes_if_have_field_coverage_settings():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
    }
    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    item = {"field1": "value1"}
    await send_item_scraped(
        spider, item
    )  # Return item to have some stats to calculate coverage

    crawler.signals.send_catch_log(
        signal=signals.spider_closed, spider=spider, reason=None
    )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_field_coverage/dict/field1") == 1.0
