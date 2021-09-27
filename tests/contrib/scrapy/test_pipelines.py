from unittest import TestCase
from slugify import slugify
from scrapy.utils.test import get_crawler
from scrapy import Item
from functools import partial

from spidermon.contrib.scrapy.pipelines import ItemValidationPipeline
from tests.fixtures.items import TreeItem, TestItem
from tests.fixtures.validators import tree_schema, test_schema, test_schema_string


STATS_AMOUNTS = "spidermon/validation/validators"
STATS_ITEM_ERRORS = "spidermon/validation/items/errors"
STATS_MISSINGS = "spidermon/validation/fields/errors/missing_required_field"
STATS_TYPES = "spidermon/validation/validators/{}/{}"

SETTING_SCHEMAS = "SPIDERMON_VALIDATION_SCHEMAS"
SETTING_MODELS = "SPIDERMON_VALIDATION_MODELS"

TREE_VALIDATOR_PATH = "tests.fixtures.validators.TreeValidator"
TEST_VALIDATOR_PATH = "tests.fixtures.validators.TestValidator"


class PipelineTestCaseMetaclass(type):
    """
    Dynamically creates test methods per every DataTest entry.

    Define class attr called `data_tests` with a list of DataTest
    objects like:

        data_tests = [
            DataTest(
                name="check validator",
                item=TestItem(),
                settings={
                    SETTING_SCHEMAS: [test_schema,],
                },
                cases=[
                    "'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
                ],
            ),
        ]
    """

    def __new__(mcs, name, bases, attrs):
        def _test_function(data_test):
            def _function(self):
                crawler = get_crawler(settings_dict=data_test.settings)
                pipe = ItemValidationPipeline.from_crawler(crawler)
                pipe.process_item(data_test.item, None)
                kwargs = {"stats": "pipe.stats.stats.get_stats()"}
                cases = data_test.cases
                for case in cases if type(cases) in [list, tuple] else [cases]:
                    assert eval(case.format(**kwargs))

            return _function

        cls = super().__new__(mcs, name, bases, attrs)
        for dt in getattr(cls, "data_tests", []):
            function_name = "test_%s" % slugify(dt.name, separator="_").lower()
            setattr(cls, function_name, _test_function(dt))
        return cls


class PipelineTest(TestCase, metaclass=PipelineTestCaseMetaclass):
    data_tests = []


class DataTest:
    def __init__(self, name, item, cases, settings=dict(), spidermon_enabled=True):
        self.name = name
        self.item = item
        self.cases = cases
        self.settings = settings
        self.settings["SPIDERMON_ENABLED"] = spidermon_enabled


def assert_type_in_stats(validator_type, obj):
    return "'{}' in {{stats}}".format(
        STATS_TYPES.format(obj.__name__.lower(), validator_type)
    )


class PipelineJSONSchemaValidator(PipelineTest):
    assert_type_in_stats = partial(assert_type_in_stats, "jsonschema")

    data_tests = [
        DataTest(
            name="processing usual items without errors",
            item=TestItem({"url": "example.com"}),
            settings={SETTING_SCHEMAS: [test_schema]},
            cases=[
                f"'{STATS_ITEM_ERRORS}' not in {{stats}}",
                f"{{stats}}['{STATS_AMOUNTS}'] is 1",
                assert_type_in_stats(Item),
            ],
        ),
        DataTest(
            name="processing nested items without errors",
            item=TreeItem({"child": TreeItem()}),
            settings={SETTING_SCHEMAS: [tree_schema]},
            cases=f"'{STATS_ITEM_ERRORS}' not in {{stats}}",
        ),
        DataTest(
            name="missing required fields",
            item=TestItem(),
            settings={SETTING_SCHEMAS: [test_schema]},
            cases=f"'{STATS_MISSINGS}' in {{stats}}",
        ),
        DataTest(
            name="validator is {} type, loads from path to a python dict".format(
                Item.__name__
            ),
            item=TestItem(),
            settings={SETTING_SCHEMAS: ["tests.fixtures.validators.test_schema"]},
            cases=[
                assert_type_in_stats(Item),
                f"'{STATS_ITEM_ERRORS}' in {{stats}}",
            ],
        ),
        DataTest(
            name="validator is {} type, loads from object path to a JSON string".format(
                Item.__name__
            ),
            item=TestItem(),
            settings={
                SETTING_SCHEMAS: ["tests.fixtures.validators.test_schema_string"]
            },
            cases=[
                assert_type_in_stats(Item),
                f"'{STATS_ITEM_ERRORS}' in {{stats}}",
            ],
        ),
        DataTest(
            name="validator is {} type, loads from a python dict".format(
                TestItem.__name__
            ),
            item=TestItem(),
            settings={SETTING_SCHEMAS: {TestItem: test_schema}},
            cases=[
                assert_type_in_stats(TestItem),
                f"'{STATS_ITEM_ERRORS}' in {{stats}}",
            ],
        ),
        DataTest(
            name="validator is {} type, loads from path to a python dict".format(
                TestItem.__name__
            ),
            item=TestItem(),
            settings={
                SETTING_SCHEMAS: {TestItem: "tests.fixtures.validators.test_schema"}
            },
            cases=[
                assert_type_in_stats(TestItem),
                f"'{STATS_ITEM_ERRORS}' in {{stats}}",
            ],
        ),
        DataTest(
            name="validator is {} type, loads from object path to a JSON string".format(
                TestItem.__name__
            ),
            item=TestItem(),
            settings={
                SETTING_SCHEMAS: {
                    TestItem: "tests.fixtures.validators.test_schema_string"
                }
            },
            cases=[
                assert_type_in_stats(TestItem),
                f"'{STATS_ITEM_ERRORS}' in {{stats}}",
            ],
        ),
        DataTest(
            name="validator is {} type, validators are in a list repr".format(
                TestItem.__name__
            ),
            item=TestItem(),
            settings={SETTING_SCHEMAS: {TestItem: [test_schema]}},
            cases=[
                assert_type_in_stats(TestItem),
                f"'{STATS_ITEM_ERRORS}' in {{stats}}",
            ],
        ),
        DataTest(
            name="support several schema validators per item",
            item=TestItem(),
            settings={SETTING_SCHEMAS: {TestItem: [test_schema, tree_schema]}},
            cases=[
                f"{{stats}}['{STATS_AMOUNTS}'] is 2",
                f"{{stats}}['{STATS_ITEM_ERRORS}'] is 2",
            ],
        ),
        DataTest(
            name="item of one type processed only by proper validator",
            item=TestItem({"url": "example.com"}),
            settings={SETTING_SCHEMAS: {TestItem: test_schema, TreeItem: tree_schema}},
            cases=f"'{STATS_ITEM_ERRORS}' not in {{stats}}",
        ),
        DataTest(
            name="each item processed by proper validator",
            item=TreeItem(),
            settings={SETTING_SCHEMAS: {TestItem: test_schema, TreeItem: tree_schema}},
            cases=[
                f"{{stats}}['{STATS_MISSINGS}'] is 1",
                assert_type_in_stats(TestItem),
                assert_type_in_stats(TreeItem),
            ],
        ),
    ]


def test_validator_from_url(mocker):
    mocked_get_contents = mocker.patch(
        "spidermon.contrib.validation.jsonschema.tools.get_contents",
        return_value=test_schema_string,
    )
    settings = {
        "SPIDERMON_ENABLED": True,
        SETTING_SCHEMAS: {TestItem: "https://fixtures.com/testschema.json"},
    }
    test_item = TestItem()
    crawler = get_crawler(settings_dict=settings)
    pipe = ItemValidationPipeline.from_crawler(crawler)
    pipe.process_item(test_item, None)
    kwargs = {"stats": "pipe.stats.stats.get_stats()"}
    stats = pipe.stats.stats.get_stats()
    assert "spidermon/validation/items/errors" in stats
    assert stats.get("spidermon/validation/validators/testitem/jsonschema", False)


class PipelineModelValidator(PipelineTest):
    assert_type_in_stats = partial(assert_type_in_stats, "schematics")

    data_tests = [
        DataTest(
            name="processing usual item without errors",
            item=TestItem({"url": "http://example.com"}),
            settings={SETTING_MODELS: [TEST_VALIDATOR_PATH]},
            cases=[
                f"'{STATS_ITEM_ERRORS}' not in {{stats}}",
                f"{{stats}}['{STATS_AMOUNTS}'] is 1",
                assert_type_in_stats(Item),
            ],
        ),
        DataTest(
            name="processing item with url problem",
            item=TestItem({"url": "example.com"}),
            settings={SETTING_MODELS: [TEST_VALIDATOR_PATH]},
            cases=f"'{STATS_ITEM_ERRORS}' in {{stats}}",
        ),
        DataTest(
            name="processing nested items without errors",
            item=TreeItem({"child": TreeItem()}),
            settings={SETTING_MODELS: [TREE_VALIDATOR_PATH]},
            cases=[
                f"'{STATS_ITEM_ERRORS}' not in {{stats}}",
                f"{{stats}}['{STATS_AMOUNTS}'] is 1",
                assert_type_in_stats(Item),
            ],
        ),
        DataTest(
            name="missing required fields",
            item=TestItem(),
            settings={SETTING_MODELS: [TEST_VALIDATOR_PATH]},
            cases=f"'{STATS_MISSINGS}' in {{stats}}",
        ),
        DataTest(
            name="validator is {} type, validators in list repr".format(
                TestItem.__name__
            ),
            item=TestItem(),
            settings={SETTING_MODELS: {TestItem: [TEST_VALIDATOR_PATH]}},
            cases=[
                f"'{STATS_ITEM_ERRORS}' in {{stats}}",
                assert_type_in_stats(TestItem),
            ],
        ),
        DataTest(
            name="support several schema validators per item",
            item=TestItem(),
            settings={
                SETTING_MODELS: {TestItem: [TEST_VALIDATOR_PATH, TREE_VALIDATOR_PATH]}
            },
            cases=[
                f"{{stats}}['{STATS_AMOUNTS}'] is 2",
                f"{{stats}}['{STATS_ITEM_ERRORS}'] is 2",
            ],
        ),
        DataTest(
            name="item of one type processed only by proper validator",
            item=TestItem({"url": "http://example.com"}),
            settings={
                SETTING_MODELS: {
                    TestItem: TEST_VALIDATOR_PATH,
                    TreeItem: TREE_VALIDATOR_PATH,
                }
            },
            cases=f"'{STATS_ITEM_ERRORS}' not in {{stats}}",
        ),
        DataTest(
            name="each item processed by proper validator",
            item=TreeItem(),
            settings={
                SETTING_MODELS: {
                    TestItem: TEST_VALIDATOR_PATH,
                    TreeItem: TREE_VALIDATOR_PATH,
                }
            },
            cases=[
                f"{{stats}}['{STATS_MISSINGS}'] is 1",
                assert_type_in_stats(TestItem),
                assert_type_in_stats(TreeItem),
            ],
        ),
    ]


class PipelineValidators(PipelineTest):

    data_tests = [
        DataTest(
            name=f"there are both validators per {Item.__name__} type",
            item=TestItem(),
            settings={
                SETTING_SCHEMAS: [test_schema],
                SETTING_MODELS: [TEST_VALIDATOR_PATH],
            },
            cases=[
                f"{{stats}}['{STATS_AMOUNTS}'] is 2",
                f"{{stats}}['{STATS_ITEM_ERRORS}'] is 2",
                assert_type_in_stats("jsonschema", Item),
                assert_type_in_stats("schematics", Item),
            ],
        ),
        DataTest(
            name="proper validators handle only related items",
            item=TestItem({"url": "http://example.com"}),
            settings={
                SETTING_SCHEMAS: {TestItem: test_schema, TreeItem: tree_schema},
                SETTING_MODELS: {Item: TEST_VALIDATOR_PATH},
            },
            cases=[
                f"{{stats}}['{STATS_AMOUNTS}'] is 3",
                f"'{STATS_ITEM_ERRORS}' not in {{stats}}",
                assert_type_in_stats("jsonschema", TestItem),
                assert_type_in_stats("jsonschema", TreeItem),
                assert_type_in_stats("schematics", Item),
            ],
        ),
    ]
