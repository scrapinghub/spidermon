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

    return Spider.from_crawler(crawler, "example.com")


async def send_item_scraped(spider, item):
    if hasattr(spider.crawler.signals, "send_catch_log_async"):
        await spider.crawler.signals.send_catch_log_async(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )
    else:
        await spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
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
            "field4": {
                "field4.1": {
                    "field4.1.1": "value",
                    "field4.1.2": "value",
                    "field4.1.3": {"field4.1.3.1": "value"},
                },
            },
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
    assert stats.get("spidermon_item_scraped_count/dict/field4") == 1
    assert stats.get("spidermon_item_scraped_count/dict/field4/field4.1") == 1
    assert (
        stats.get("spidermon_item_scraped_count/dict/field4/field4.1/field4.1.1") == 1
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field4/field4.1/field4.1.2") == 1
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field4/field4.1/field4.1.3") == 1
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field4/field4.1/field4.1.3/field4.1.3.1",
        )
        == 1
    )


@deferred_f_from_coro_f
async def test_item_scraped_count_multiple_nested_field_with_limit():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_DICT_FIELDS_COVERAGE_LEVELS": 1,
    }
    returned_items = [
        {
            "field1": {"field1.1": "value1.1"},
            "field2": "value2",
            "field3": {"field3.1": "value3.1"},
            "field4": {
                "field4.1": {
                    "field4.1.1": "value",
                    "field4.1.2": "value",
                    "field4.1.3": {"field4.1.3.1": "value"},
                },
            },
        },
        {
            "field1": {
                "field1.1": "value1.1",
                "field1.2": "value1.2",
            },
            "field2": "value2",
        },
    ]
    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")
    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.2") == 1
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field3") == 1
    assert (
        stats.get("spidermon_item_scraped_count/dict/field4/field4.1/field4.1.1")
        is None
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field4/field4.1/field4.1.2")
        is None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field4/field4.1/field4.1.3/field4.1.3.1",
        )
        is None
    )


@deferred_f_from_coro_f
async def test_item_scraped_count_multiple_nested_field_with_two_levels_limit():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_DICT_FIELDS_COVERAGE_LEVELS": 2,
    }
    returned_items = [
        {
            "field1": {"field1.1": "value1.1"},
            "field2": "value2",
            "field3": {"field3.1": "value3.1"},
            "field4": {
                "field4.1": {
                    "field4.1.1": "value",
                    "field4.1.2": "value",
                    "field4.1.3": {"field4.1.3.1": "value"},
                },
            },
        },
        {
            "field1": {
                "field1.1": "value1.1",
                "field1.2": "value1.2",
            },
            "field2": "value2",
        },
    ]
    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")
    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.2") == 1
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field3") == 1
    assert (
        stats.get("spidermon_item_scraped_count/dict/field4/field4.1/field4.1.1") == 1
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field4/field4.1/field4.1.2") == 1
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field4/field4.1/field4.1.3/field4.1.3.1",
        )
        is None
    )


@deferred_f_from_coro_f
async def test_item_scraped_count_multiple_nested_field_with_no_nested_levels():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_DICT_FIELDS_COVERAGE_LEVELS": 0,
    }
    returned_items = [
        {
            "field1": {"field1.1": "value1.1"},
            "field2": "value2",
            "field3": {"field3.1": "value3.1"},
            "field4": {
                "field4.1": {
                    "field4.1.1": "value",
                    "field4.1.2": "value",
                    "field4.1.3": {"field4.1.3.1": "value"},
                },
            },
        },
        {
            "field1": {
                "field1.1": "value1.1",
                "field1.2": "value1.2",
            },
            "field2": "value2",
        },
    ]
    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")
    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.1") is None
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.2") is None
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field3") == 1
    assert (
        stats.get("spidermon_item_scraped_count/dict/field4/field4.1/field4.1.1")
        is None
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field4/field4.1/field4.1.2")
        is None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field4/field4.1/field4.1.3/field4.1.3.1",
        )
        is None
    )


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
        spider,
        item,
    )  # Return item to have some stats to calculate coverage

    crawler.signals.send_catch_log(
        signal=signals.spider_closed,
        spider=spider,
        reason=None,
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
        spider,
        item,
    )  # Return item to have some stats to calculate coverage

    crawler.signals.send_catch_log(
        signal=signals.spider_closed,
        spider=spider,
        reason=None,
    )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_field_coverage/dict/field1") == 1.0


@deferred_f_from_coro_f
async def test_item_scraped_count_ignore_none_values():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_SKIP_NONE": True,
    }

    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    returned_items = [
        {"field1": "value1", "field2": "value2"},
        {"field1": "value1", "field2": None},
    ]

    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 1


@deferred_f_from_coro_f
async def test_item_scraped_count_do_not_ignore_none_values():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_SKIP_NONE": False,
    }
    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    returned_items = [
        {"field1": "value1", "field2": "value2"},
        {"field1": "value1", "field2": None},
    ]

    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2


@deferred_f_from_coro_f
async def test_item_scraped_count_do_not_ignore_none_values_by_default(spider):
    returned_items = [
        {"field1": "value1", "field2": "value2"},
        {"field1": "value1", "field2": None},
    ]

    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2


@deferred_f_from_coro_f
async def test_item_scraped_count_list_of_dicts_disabled(spider):
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_LIST_FIELDS_COVERAGE_LEVELS": 0,
    }
    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")
    returned_items = [
        {
            "field1": 1,
            "field2": [
                {
                    "nested_field1": 1,
                    "nested_field2": 1,
                    "nested_field3": [
                        {"deep_field1": 1},
                        {"deep_field1": 1},
                        {"deep_field2": 1},
                    ],
                },
                {"nested_field2": 1},
            ],
        },
        {
            "field1": 1,
            "field2": [
                {"nested_field1": 1},
                {
                    "nested_field1": 1,
                    "nested_field4": {"deep_field1": 1, "deep_field2": 1},
                },
                {"nested_field1": 1, "nested_field2": 1},
            ],
        },
    ]

    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2

    assert stats.get("spidermon_item_scraped_count/dict/field2/_items") is None
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field1")
        is None
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field2")
        is None
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field3")
        is None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items",
        )
        is None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field1",
        )
        is None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field2",
        )
        is None
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field4")
        is None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field1",
        )
        is None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field2",
        )
        is None
    )


@deferred_f_from_coro_f
async def test_item_scraped_count_list_of_dicts_one_nesting_level(spider):
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_LIST_FIELDS_COVERAGE_LEVELS": 1,
    }
    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")
    returned_items = [
        {
            "field1": 1,
            "field2": [
                {
                    "nested_field1": 1,
                    "nested_field2": 1,
                    "nested_field3": [
                        {"deep_field1": 1},
                        {"deep_field1": 1},
                        {"deep_field2": 1},
                    ],
                },
                {"nested_field2": 1},
            ],
        },
        {
            "field1": 1,
            "field2": [
                {"nested_field1": 1},
                {
                    "nested_field1": 1,
                    "nested_field4": {"deep_field1": 1, "deep_field2": 1},
                },
                {"nested_field1": 1, "nested_field2": 1},
            ],
        },
    ]

    for item in returned_items:
        await send_item_scraped(spider, item)

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2

    assert stats.get("spidermon_item_scraped_count/dict/field2/_items") == 5
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field1") == 4
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field2") == 3
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field3") == 1
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items",
        )
        is None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field1",
        )
        is None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field2",
        )
        is None
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field4") == 1
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field1",
        )
        == 1
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field2",
        )
        == 1
    )


@deferred_f_from_coro_f
async def test_item_scraped_count_list_of_dicts_two_nesting_levels(spider):
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_LIST_FIELDS_COVERAGE_LEVELS": 2,
    }
    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")
    returned_items = [
        {
            "field1": 1,
            "field2": [
                {
                    "nested_field1": 1,
                    "nested_field2": 1,
                    "nested_field3": [
                        {"deep_field1": 1},
                        {"deep_field1": 1},
                        {"deep_field2": 1},
                    ],
                },
                {"nested_field2": 1},
            ],
        },
        {
            "field1": 1,
            "field2": [
                {"nested_field1": 1},
                {
                    "nested_field1": 1,
                    "nested_field4": {"deep_field1": 1, "deep_field2": 1},
                },
                {"nested_field1": 1, "nested_field2": 1},
            ],
        },
    ]

    async def send_signal(item):
        if hasattr(spider.crawler.signals, "send_catch_log_async"):
            await spider.crawler.signals.send_catch_log_async(
                signal=signals.item_scraped,
                item=item,
                response="",
                spider=spider,
            )
        else:
            spider.crawler.signals.send_catch_log_deferred(
                signal=signals.item_scraped,
                item=item,
                response="",
                spider=spider,
            )

    for item in returned_items:
        await send_signal(item)

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2

    assert stats.get("spidermon_item_scraped_count/dict/field2/_items") == 5
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field1") == 4
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field2") == 3
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field3") == 1
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items",
        )
        == 3
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field1",
        )
        == 2
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field2",
        )
        == 1
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field4") == 1
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field1",
        )
        == 1
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field2",
        )
        == 1
    )
