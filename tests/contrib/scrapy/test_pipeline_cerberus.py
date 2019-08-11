from __future__ import absolute_import
from scrapy.utils.test import get_crawler
from scrapy import Item

import pytest
from spidermon.contrib.scrapy.pipelines import ItemValidationPipeline
from tests.fixtures.items import TestItem, TreeItem
from tests.fixtures.validators import (
    cerberus_tree_schema,
    cerberus_test_schema,
    cerberus_error_test_schema,
)

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
        # DataTest(
        #     name="validator is {} type, loads from path to a python dict".format(
        #         Item.__name__
        #     ),
        #     item=TestItem(),
        #     settings={SETTING_CERBERUS: ["tests.fixtures.validators.test_schema"]},
        #     cases=[
        #         assert_type_in_stats(Item),
        #         "'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
        #     ],
        # ),
        # DataTest(
        #     name="validator is {} type, loads from a python dict".format(
        #         TestItem.__name__
        #     ),
        #     item=TestItem(),
        #     settings={SETTING_CERBERUS: {TestItem: test_schema}},
        #     cases=[
        #         assert_type_in_stats(TestItem),
        #         "'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
        #     ],
        # ),
        # DataTest(
        #     name="validator is {} type, loads from path to a python dict".format(
        #         TestItem.__name__
        #     ),
        #     item=TestItem(),
        #     settings={
        #         SETTING_CERBERUS: {TestItem: "tests.fixtures.validators.test_schema"}
        #     },
        #     cases=[
        #         assert_type_in_stats(TestItem),
        #         "'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
        #     ],
        # ),
        # DataTest(
        #     name="validator is {} type, loads from object path to a JSON string".format(
        #         TestItem.__name__
        #     ),
        #     item=TestItem(),
        #     settings={
        #         SETTING_CERBERUS: {
        #             TestItem: "tests.fixtures.validators.test_schema_string"
        #         }
        #     },
        #     cases=[
        #         assert_type_in_stats(TestItem),
        #         "'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
        #     ],
        # ),
        # DataTest(
        #     name="validator is {} type, validators are in a list repr".format(
        #         TestItem.__name__
        #     ),
        #     item=TestItem(),
        #     settings={SETTING_CERBERUS: {TestItem: [test_schema]}},
        #     cases=[
        #         assert_type_in_stats(TestItem),
        #         "'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
        #     ],
        # ),
        pytest.param(
            TreeItem(),
            {SETTING_CERBERUS: [cerberus_test_schema]},
            ["{}".format(STATS_MISSINGS)],
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
            ["{}".format(STATS_ITEM_ERRORS)],
            id="processing usual items without errors",
        ),
        pytest.param(
            TreeItem({
                "quotes": {"author": "Vipul Gupta", "quote": "Life is vanilla"},
                "child": "https://example.com",
            }),
            {SETTING_CERBERUS: [cerberus_tree_schema]},
            ["{}".format(STATS_ITEM_ERRORS)],
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
            ["{}".format(STATS_AMOUNTS)],
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

        # def test_check_amount():


#     item = TestItem({"url": "example.com"})
#     settings =  {SETTING_CERBERUS: [cerberus_test_schema]}
#     crawler = get_crawler(settings_dict=settings)
#     pipe = ItemValidationPipeline.from_crawler(crawler)
#     pipe.process_item(item, None)
#     stats = pipe.stats.stats.get_stats()
#     assert "{1}['{2}'] is 1".format(stats, STATS_AMOUNTS),


# "{{stats}}['{}'] is 1".format(STATS_AMOUNTS),
