from __future__ import absolute_import
from slugify import slugify
from scrapy.utils.test import get_crawler
from scrapy import Item
from functools import partial
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

def assert_type_in_stats(validator_type, obj):
    return "'{}' in {{stats}}".format(
        STATS_TYPES.format(obj.__name__.lower(), validator_type)
    )

ASSERT_TYPE_IN_STATS = partial(assert_type_in_stats, "cerberus")


@pytest.mark.parametrize(
    "item,settings,cases",
    [
        pytest.param(
            TestItem({"url": "example.com"}),
            {SETTING_CERBERUS: [cerberus_test_schema]},
            [
                "'{}' not in {{stats}}".format(STATS_ITEM_ERRORS),
                "{{stats}}['{}'] is 1".format(STATS_AMOUNTS),
                ASSERT_TYPE_IN_STATS(Item),
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
    kwargs = {"stats":"pipe.stats.stats.get_stats()"}
    for case in cases if type(cases) in [list, tuple] else [cases]:
        assert eval(case.format(**kwargs))
