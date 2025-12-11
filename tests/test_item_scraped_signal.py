import pytest
from scrapy import Item, signals
from scrapy.spiders import Spider
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
            signal=signals.item_scraped,
            item=Item(),
            response="",
            spider=spider,
        )

    for _ in range(25):
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=TestItem(),
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count") == 60
    assert stats.get("spidermon_item_scraped_count/dict") == 15
    assert stats.get("spidermon_item_scraped_count/Item") == 20
    assert stats.get("spidermon_item_scraped_count/TestItem") == 25


def test_item_scraped_count_single_field(spider):
    returned_items = [{"field1": "value1"}]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 1


def test_item_scraped_count_multiple_field(spider):
    returned_items = [{"field1": "value1", "field2": "value2"}]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 1
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 1


def test_item_scraped_count_multiple_items(spider):
    returned_items = [
        {"field1": "value1", "field2": "value2"},
        {"field1": "value1", "field2": "value2"},
    ]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2


def test_item_scraped_count_multiple_items_field_missing(spider):
    returned_items = [
        {"field1": "value1", "field2": "value2"},
        {
            "field1": "value1",
        },
    ]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 1


def test_item_scraped_count_single_nested_field(spider):
    returned_items = [{"field1": {"field1.1": "value1.1"}}]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()
    assert stats.get("spidermon_item_scraped_count/dict") == 1
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 1
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.1") == 1


def test_item_scraped_count_multiple_nested_field(spider):
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
                }
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
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

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
            "spidermon_item_scraped_count/dict/field4/field4.1/field4.1.3/field4.1.3.1"
        )
        == 1
    )


def test_item_scraped_count_multiple_nested_field_with_limit():
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
                }
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
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.2") == 1
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field3") == 1
    assert (
        stats.get("spidermon_item_scraped_count/dict/field4/field4.1/field4.1.1")
        == None
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field4/field4.1/field4.1.2")
        == None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field4/field4.1/field4.1.3/field4.1.3.1"
        )
        == None
    )


def test_item_scraped_count_multiple_nested_field_with_two_levels_limit():
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
                }
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
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

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
            "spidermon_item_scraped_count/dict/field4/field4.1/field4.1.3/field4.1.3.1"
        )
        == None
    )


def test_item_scraped_count_multiple_nested_field_with_no_nested_levels():
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
                }
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
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.1") == None
    assert stats.get("spidermon_item_scraped_count/dict/field1/field1.2") == None
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field3") == 1
    assert (
        stats.get("spidermon_item_scraped_count/dict/field4/field4.1/field4.1.1")
        == None
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field4/field4.1/field4.1.2")
        == None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field4/field4.1/field4.1.3/field4.1.3.1"
        )
        == None
    )


def test_do_not_add_field_coverage_when_spider_closes_if_do_not_have_field_coverage_settings():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": False,
    }
    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    item = {"field1": "value1"}
    spider.crawler.signals.send_catch_log_deferred(
        signal=signals.item_scraped,
        item=item,
        response="",
        spider=spider,
    )  # Return item to have some stats to calculate coverage

    crawler.signals.send_catch_log(
        signal=signals.spider_closed, spider=spider, reason=None
    )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_field_coverage/dict/field1") is None


def test_add_field_coverage_when_spider_closes_if_have_field_coverage_settings():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
    }
    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    item = {"field1": "value1"}
    spider.crawler.signals.send_catch_log_deferred(
        signal=signals.item_scraped,
        item=item,
        response="",
        spider=spider,
    )  # Return item to have some stats to calculate coverage

    crawler.signals.send_catch_log(
        signal=signals.spider_closed, spider=spider, reason=None
    )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_field_coverage/dict/field1") == 1.0


def test_item_scraped_count_ignore_none_values():
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
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 1


def test_item_scraped_count_do_not_ignore_none_values():
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
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2


def test_item_scraped_count_do_not_ignore_none_values_by_default(spider):
    returned_items = [
        {"field1": "value1", "field2": "value2"},
        {"field1": "value1", "field2": None},
    ]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2


def test_item_scraped_count_ignore_custom_skip_values():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_SKIP_VALUES": ["N/A", "-", "TBD"],
    }

    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    returned_items = [
        {"field1": "value1", "field2": "N/A", "field3": "value3"},
        {"field1": "value1", "field2": "-", "field3": "TBD"},
        {"field1": "value1", "field2": "value2", "field3": "value3"},
    ]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 3
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2") == 1
    )  # Only the valid value
    assert (
        stats.get("spidermon_item_scraped_count/dict/field3") == 2
    )  # Only the valid values (skipped "TBD")


def test_item_scraped_count_ignore_default_skip_values():
    """Test that default skip values (empty string, empty list, empty dict, N/A, -) are applied"""
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
    }

    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    returned_items = [
        {"field1": "value1", "field2": "N/A", "field3": "-", "field4": ""},
        {"field1": "value1", "field2": "value2", "field3": "value3", "field4": "value4"},
    ]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 1  # "N/A" skipped by default
    assert stats.get("spidermon_item_scraped_count/dict/field3") == 1  # "-" skipped by default
    assert stats.get("spidermon_item_scraped_count/dict/field4") == 1  # "" skipped by default


def test_item_scraped_count_do_not_ignore_custom_skip_values_when_empty_list():
    """Test that setting skip_values to empty list disables default skip values"""
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_SKIP_VALUES": [],
    }

    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    returned_items = [
        {"field1": "value1", "field2": "N/A"},
        {"field1": "value1", "field2": "-"},
    ]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2") == 2
    )  # Counted because skip_values is empty list


def test_item_scraped_count_skip_values_type_sensitive():
    """Test that skip_values matching is type-sensitive (string "0" != int 0)"""
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_SKIP_VALUES": ["0", 0],
    }

    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    returned_items = [
        {"field1": "0", "field2": 0, "field3": "value"},
        {"field1": "value", "field2": 1, "field3": "value"},
    ]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    # Both "0" and 0 should be skipped
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 1  # Only "value"
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 1  # Only 1
    assert stats.get("spidermon_item_scraped_count/dict/field3") == 2


def test_item_scraped_count_skip_integer_values():
    """Test that integer values like 0 and -1 can be skipped"""
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_SKIP_VALUES": [0, -1],
    }

    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    returned_items = [
        {"field1": 0, "field2": -1, "field3": 42},
        {"field1": 1, "field2": 2, "field3": 42},
    ]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    # Integer 0 and -1 should be skipped
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 1  # Only 1
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 1  # Only 2
    assert stats.get("spidermon_item_scraped_count/dict/field3") == 2  # Both 42 values


def test_item_scraped_count_skip_values_with_json_string():
    """Test that JSON string format preserves types for non-string values"""
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_SKIP_VALUES": '[0, -1, "N/A"]',
    }

    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    returned_items = [
        {"field1": 0, "field2": -1, "field3": "N/A", "field4": "value"},
        {"field1": 1, "field2": 2, "field3": "value", "field4": "value"},
    ]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    # Integer 0, -1, and string "N/A" should all be skipped
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 1  # Only 1
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 1  # Only 2
    assert stats.get("spidermon_item_scraped_count/dict/field3") == 1  # Only "value"
    assert stats.get("spidermon_item_scraped_count/dict/field4") == 2  # Both "value"


def test_item_scraped_count_skip_values_works_with_nested_fields():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_SKIP_VALUES": ["N/A"],
    }

    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    returned_items = [
        {"field1": {"nested1": "value", "nested2": "N/A"}},
        {"field1": {"nested1": "value", "nested2": "value"}},
    ]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field1/nested1") == 2
    assert (
        stats.get("spidermon_item_scraped_count/dict/field1/nested2") == 1
    )  # Only the valid value


def test_item_scraped_count_skip_values_works_with_skip_falsy():
    """Test that skip_values works alongside skip_falsy"""
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_SKIP_FALSY": True,
        "SPIDERMON_FIELD_COVERAGE_SKIP_VALUES": ["N/A"],
    }

    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")

    returned_items = [
        {"field1": "", "field2": "N/A", "field3": "value"},
        {"field1": "value", "field2": "value", "field3": "value"},
    ]

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    # Both empty string (falsy) and "N/A" (skip_values) should be skipped
    assert stats.get("spidermon_item_scraped_count/dict/field1") == 1  # Only "value"
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 1  # Only "value"
    assert stats.get("spidermon_item_scraped_count/dict/field3") == 2


def test_item_scraped_count_list_of_dicts_disabled(spider):
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
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

    stats = spider.crawler.stats.get_stats()

    assert stats.get("spidermon_item_scraped_count/dict/field1") == 2
    assert stats.get("spidermon_item_scraped_count/dict/field2") == 2

    assert stats.get("spidermon_item_scraped_count/dict/field2/_items") == None
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field1")
        == None
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field2")
        == None
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field3")
        == None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items"
        )
        == None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field1"
        )
        == None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field2"
        )
        == None
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field4")
        == None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field1"
        )
        == None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field2"
        )
        == None
    )


def test_item_scraped_count_list_of_dicts_one_nesting_level(spider):
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
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

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
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items"
        )
        == None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field1"
        )
        == None
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field2"
        )
        == None
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field4") == 1
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field1"
        )
        == 1
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field2"
        )
        == 1
    )


def test_item_scraped_count_list_of_dicts_two_nesting_levels(spider):
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

    for item in returned_items:
        spider.crawler.signals.send_catch_log_deferred(
            signal=signals.item_scraped,
            item=item,
            response="",
            spider=spider,
        )

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
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items"
        )
        == 3
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field1"
        )
        == 2
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field2"
        )
        == 1
    )
    assert (
        stats.get("spidermon_item_scraped_count/dict/field2/_items/nested_field4") == 1
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field1"
        )
        == 1
    )
    assert (
        stats.get(
            "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field2"
        )
        == 1
    )
