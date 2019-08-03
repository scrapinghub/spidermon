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
    return "'{}' in {{stats}}".format(
        STATS_TYPES.format(obj.__name__.lower(), "cerberus")
    )


@pytest.mark.parametrize(
    "item,settings,cases",
    [
        pytest.param(
            TestItem({"url": "example.com"}),
            {SETTING_CERBERUS: [cerberus_test_schema]},
            [
                "'{}' not in {{stats}}".format(STATS_ITEM_ERRORS),
                "{{stats}}['{}'] is 1".format(STATS_AMOUNTS),
                assert_in_cerberus_stats(Item),
            ],
            id="processing usual items without errors",
        ),
        pytest.param(
            TreeItem(),
            {SETTING_CERBERUS: [cerberus_tree_schema]},
            "'{}' in {{stats}}".format(STATS_MISSINGS),
            id="missing required fields",
        ),
    ],
)
def test_get_crawler_only(item, settings, cases):
    crawler = get_crawler(settings_dict=settings)
    pipe = ItemValidationPipeline.from_crawler(crawler)
    pipe.process_item(item, None)
    kwargs = {"stats": "pipe.stats.stats.get_stats()"}
    for case in cases:
        pass
        # FIXX THISS
        # lambda x: case.format(**x)


def test_cerberus_from_pipeline(mocker):
    # mocked_get_contents = mocker.patch(
    #     "spidermon.contrib.validation.utils.get_schema_from",
    #     return_value=cerberus_error_test_schema,
    # )
    settings = {SETTING_CERBERUS: [cerberus_error_test_schema]}
    #     TestItem: {ScrapingHub"}
    # }
    test_item = {"url":"asd", "title":"wdad"}
    crawler = get_crawler(settings_dict=settings)
    pipe = ItemValidationPipeline.from_crawler(crawler)
    pipe.process_item(test_item, None)
    kwargs = {"stats": "pipe.stats.stats.get_stats()"}
    stats = pipe.stats.stats.get_stats()
    assert "spidermon/validation/items/errors" in stats
    assert "spidermon/validation/fields/errors/invalid_number" in stats
    assert stats.get("spidermon/validation/validators/testitem/cerberus", True)
