from __future__ import absolute_import
import sys
import os
import pytest
from scrapy.utils.test import get_crawler
from scrapy import Item
from spidermon.contrib.scrapy.pipelines import ItemValidationPipeline
from tests.fixtures.items import TestItem, TreeItem
from tests.fixtures.validators import (
    cerberus_tree_schema,
    cerberus_test_schema,
    test_cerberus_schema_string
)

STATS_ITEM_ERRORS = "spidermon/validation/items/errors"
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
            {SETTING_CERBERUS: [f'{os.getcwd()}/contrib/scrapy/schema.json']},
            [assert_in_cerberus_stats(Item), "{}".format(STATS_ITEM_ERRORS)],
            id="validator is {} type, loads from path to schema".format(Item.__name__),
        ),
        pytest.param(
            TestItem(),
            {SETTING_CERBERUS: {
                TestItem: "tests.fixtures.validators.cerberus_test_schema"
            }},
            [assert_in_cerberus_stats(TestItem), "{}".format(STATS_ITEM_ERRORS)],
            id="validator is {} type, loads from path to a python dict".format(
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
            TestItem(),
            {SETTING_CERBERUS: [cerberus_test_schema]},
            ["spidermon/validation/fields/errors/missing_required_field"],
            id="Missing required fields",
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
            id="processing simple items without errors",
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


def test_stats_amounts_in_pipeline():
    item = TestItem({"title": "ScrapingHub"})
    settings = {SETTING_CERBERUS: [cerberus_test_schema]}
    crawler = get_crawler(settings_dict=settings)
    pipe = ItemValidationPipeline.from_crawler(crawler)
    pipe.process_item(item, None)
    assert pipe.stats.stats.get_stats()["spidermon/validation/validators"] is 1
    assert pipe.stats.stats.get_stats()["spidermon/validation/fields/errors/missing_required_field"] is 1


@pytest.mark.skipif(
    sys.version_info < (3, 4), reason="mock requires python3.4 or higher"
)
def test_validation_from_url(mocker):
    mocked_get_contents = mocker.patch(
        "spidermon.contrib.validation.utils.get_contents",
        return_value=test_cerberus_schema_string,
    )
    settings = {SETTING_CERBERUS: ["https://fixtures.com/testschema.json"]}
    test_item = TestItem()
    crawler = get_crawler(settings_dict=settings)
    pipe = ItemValidationPipeline.from_crawler(crawler)
    pipe.process_item(test_item, None)

    assert "spidermon/validation/items/errors" in pipe.stats.stats.get_stats()
    assert pipe.stats.stats.get_stats().get("spidermon/validation/validators/testitem/cerberus", True)
