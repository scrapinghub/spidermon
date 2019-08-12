from __future__ import absolute_import
from scrapy.utils.test import get_crawler
from scrapy import Item
import sys
import pytest
from spidermon.contrib.scrapy.pipelines import ItemValidationPipeline
from tests.fixtures.items import TestItem, TreeItem
from tests.fixtures.validators import cerberus_tree_schema, cerberus_test_schema

STATS_AMOUNTS = "spidermon/validation/validators"
STATS_ITEM_ERRORS = "spidermon/validation/items/errors"
STATS_MISSINGS = "spidermon/validation/fields/errors/missing_required_field"
STATS_TYPES = "spidermon/validation/validators/{}/{}"
SETTING_CERBERUS = "SPIDERMON_VALIDATION_CERBERUS"


def assert_in_cerberus_stats(obj):
    return "{}".format(STATS_TYPES.format(obj.__name__.lower(), "cerberus"))


@pytest.mark.parametrize(
    "item,settings,cases",
    [
        pytest.param(
            TestItem({"url": "example.com"}),
            {SETTING_CERBERUS: [cerberus_test_schema]},
            [assert_in_cerberus_stats(Item)],
            id="processing usual items without errors",
        ),
        pytest.param(
            TestItem(),
            {SETTING_CERBERUS: {TestItem: cerberus_test_schema}},
            [assert_in_cerberus_stats(TestItem), STATS_ITEM_ERRORS],
            id="validator is {} type, loads from a python dict".format(
                TestItem.__name__
            ),
        ),
        pytest.param(
            TestItem(),
            {SETTING_CERBERUS: {TestItem: [cerberus_test_schema]}},
            [assert_in_cerberus_stats(TestItem), STATS_ITEM_ERRORS],
            id="validator is {} type, validators are in a list repr".format(
                TestItem.__name__
            ),
        ),
        pytest.param(
            TreeItem(),
            {SETTING_CERBERUS: [cerberus_test_schema]},
            [STATS_MISSINGS],
            id="missing required fields",
        ),
    ],
)
def test_stats_in_pipeline(item, settings, cases):
    crawler = get_crawler(settings_dict=settings)
    pipe = ItemValidationPipeline.from_crawler(crawler)
    pipe.process_item(item, None)
    for case in cases:
        casechecker = lambda x: x in pipe.stats.stats.get_stats()
        assert casechecker(case)


@pytest.mark.parametrize(
    "item,settings,cases",
    [
        pytest.param(
            TestItem({"url": "example.com"}),
            {SETTING_CERBERUS: [cerberus_test_schema]},
            [STATS_ITEM_ERRORS],
            id="processing usual items without errors",
        ),
        pytest.param(
            TreeItem(
                {
                    "quotes": {"author": "Vipul Gupta", "quote": "Life is vanilla"},
                    "child": "https://example.com",
                }
            ),
            {SETTING_CERBERUS: [cerberus_tree_schema]},
            [STATS_ITEM_ERRORS],
            id="processing nested items without errors",
        ),
    ],
)
def test_stats_not_in_pipeline(item, settings, cases):
    crawler = get_crawler(settings_dict=settings)
    pipe = ItemValidationPipeline.from_crawler(crawler)
    pipe.process_item(item, None)
    for case in cases:
        casechecker = lambda x: x not in pipe.stats.stats.get_stats()
        assert casechecker(case)


@pytest.mark.parametrize(
    "item,settings,cases",
    [
        pytest.param(
            TestItem({"url": "example.com"}),
            {SETTING_CERBERUS: [cerberus_test_schema]},
            [STATS_AMOUNTS],
            id="processing usual items without errors",
        )
    ],
)
def test_stats_amounts_in_pipeline(item, settings, cases):
    crawler = get_crawler(settings_dict=settings)
    pipe = ItemValidationPipeline.from_crawler(crawler)
    pipe.process_item(item, None)
    for case in cases:
        casechecker = lambda x: pipe.stats.stats.get_stats()[x] is 1
        assert casechecker(case)


# @pytest.mark.skipif(
#     sys.version_info < (3, 4), reason="mock requires python3.4 or higher"
# )
# def test_pipelines_mocked(mocker):
#     mocker_cerberus_validator = mocker.patch("")
