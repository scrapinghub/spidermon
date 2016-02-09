from unittest import TestCase
from slugify import slugify
from scrapy.utils.test import get_crawler

from spidermon.contrib.scrapy.pipelines import ItemValidationPipeline, UniversalItem
from tests.fixtures.items import TreeItem, TestItem
from tests.fixtures.validators import tree_schema, test_schema, test_schema_string


STATS_AMOUNTS = 'spidermon/validation/validators'
STATS_ITEM_ERRORS = 'spidermon/validation/items/errors'
STATS_MISSINGS = 'spidermon/validation/fields/errors/missing_required_field'
STATS_TYPES = 'spidermon/validation/validators/{}/{}'

SETTING_SCHEMAS = 'SPIDERMON_VALIDATION_SCHEMAS'
SETTING_MODELS = 'SPIDERMON_VALIDATION_MODELS'

TREE_VALIDATOR_PATH = 'tests.fixtures.validators.TreeValidator'
TEST_VALIDATOR_PATH = 'tests.fixtures.validators.TestValidator'


class PipelineTestCaseMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        def _test_function(data_test):
            def _function(self):
                crawler = get_crawler(settings_dict=data_test.settings)
                pipe = ItemValidationPipeline.from_crawler(crawler)
                pipe.process_item(data_test.item, None)
                kwargs = {
                    'stats': 'pipe.stats.stats.get_stats()',
                }
                cases = data_test.cases
                for case in cases if type(cases) in [list, tuple] else [cases]:
                    assert eval(case.format(**kwargs))
            return _function
        cls = super(PipelineTestCaseMetaclass, mcs).__new__(mcs, name, bases, attrs)
        for dt in getattr(cls, 'data_tests', []):
            function_name = 'test_%s' % slugify(dt.name, separator='_').lower()
            setattr(cls, function_name, _test_function(dt))
        return cls


class PipelineTest(TestCase):
    __metaclass__ = PipelineTestCaseMetaclass
    data_tests = []


class DataTest(object):
    def __init__(self, name, item, cases, settings={}):
        self.name = name
        self.item = item
        self.cases = cases
        self.settings = settings


class PipelineJSONSchemaValidator(PipelineTest):
    STATS_TYPES = 'spidermon/validation/validators/{}/jsonschema'

    data_tests = [
        DataTest(
            name="processing usual items without errors",
            item=TestItem({'url': 'example.com'}),
            settings={
                SETTING_SCHEMAS: [test_schema,],
            },
            cases=[
                "'{}' not in {{stats}}".format(STATS_ITEM_ERRORS),
                "{{stats}}['{}'] is 1".format(STATS_AMOUNTS),
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(UniversalItem.__name__.lower()))
            ],
        ),
        DataTest(
            name="processing nested items without errors",
            item=TreeItem({'child': TreeItem()}),
            settings={
                SETTING_SCHEMAS: [tree_schema,],
            },
            cases="'{}' not in {{stats}}".format(STATS_ITEM_ERRORS),
        ),
        DataTest(
            name="missing required fields",
            item=TestItem(),
            settings={
                SETTING_SCHEMAS: [test_schema,],
            },
            cases="'{}' in {{stats}}".format(STATS_MISSINGS),
        ),
        DataTest(
            name="validator is {} type, loads from path to a python dict".format(
                UniversalItem.__name__),
            item=TestItem(),
            settings={
                SETTING_SCHEMAS: ['tests.fixtures.validators.test_schema',],
            },
            cases=[
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(UniversalItem.__name__.lower())),
                "'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
            ],
        ),
        DataTest(
            name="validator is {} type, loads from object path to a JSON string".format(
                UniversalItem.__name__),
            item=TestItem(),
            settings={
                SETTING_SCHEMAS: ['tests.fixtures.validators.test_schema_string',],
            },
            cases=[
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(UniversalItem.__name__.lower())),
                "'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
            ],
        ),
        DataTest(
            name="validator is {} type, loads from a python dict".format(
                TestItem.__name__),
            item=TestItem(),
            settings={
                SETTING_SCHEMAS: {
                    TestItem: test_schema,
                }
            },
            cases=[
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(TestItem.__name__.lower())),
                "'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
            ],
        ),
        DataTest(
            name="validator is {} type, loads from path to a python dict".format(
                TestItem.__name__),
            item=TestItem(),
            settings={
                SETTING_SCHEMAS: {
                    TestItem: 'tests.fixtures.validators.test_schema',
                }
            },
            cases=[
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(TestItem.__name__.lower())),
                "'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
            ],
        ),
        DataTest(
            name="validator is {} type, loads from object path to a JSON string".format(
                TestItem.__name__),
            item=TestItem(),
            settings={
                SETTING_SCHEMAS: {
                    TestItem: 'tests.fixtures.validators.test_schema_string',
                }
            },
            cases=[
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(TestItem.__name__.lower())),
                "'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
            ],
        ),
        DataTest(
            name="validator is {} type, validators are in a list repr".format(
                TestItem.__name__),
            item=TestItem(),
            settings={
                SETTING_SCHEMAS: {
                    TestItem: [test_schema],
                }
            },
            cases=[
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(TestItem.__name__.lower())),
                "'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
            ],
        ),
        DataTest(
            name="support several schema validators per item",
            item=TestItem(),
            settings={
                SETTING_SCHEMAS: {
                    TestItem: [
                        test_schema,
                        tree_schema,
                    ],
                }
            },
            cases=[
                "{{stats}}['{}'] is 2".format(STATS_AMOUNTS),
                "{{stats}}['{}'] is 2".format(STATS_ITEM_ERRORS),
            ],
        ),
        DataTest(
            name="item of one type processed only by proper validator",
            item=TestItem({'url': 'example.com'}),
            settings={
                SETTING_SCHEMAS: {
                    TestItem: test_schema,
                    TreeItem: tree_schema,
                }
            },
            cases="'{}' not in {{stats}}".format(STATS_ITEM_ERRORS),
        ),
        DataTest(
            name="each item processed by proper validator",
            item=TreeItem(),
            settings={
                SETTING_SCHEMAS: {
                    TestItem: test_schema,
                    TreeItem: tree_schema,
                }
            },
            cases=[
                "{{stats}}['{}'] is 1".format(STATS_MISSINGS),
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(TestItem.__name__.lower())),
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(TreeItem.__name__.lower())),
            ],
        ),
        DataTest(
            name="item should be processed by both validators",
            item=TestItem({'url': 'example.com'}),
            settings={
                SETTING_SCHEMAS: {
                    TestItem: test_schema,
                    UniversalItem: tree_schema,
                }
            },
            cases="'{}' in {{stats}}".format(STATS_MISSINGS),
        ),
    ]

class PipelineModelValidator(PipelineTest):
    STATS_TYPES = 'spidermon/validation/validators/{}/schematics'

    data_tests = [
        DataTest(
            name="processing usual item without errors",
            item=TestItem({'url': 'http://example.com'}),
            settings={
                SETTING_MODELS: [TEST_VALIDATOR_PATH,],
            },
            cases=[
                "'{}' not in {{stats}}".format(STATS_ITEM_ERRORS),
                "{{stats}}['{}'] is 1".format(STATS_AMOUNTS),
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(UniversalItem.__name__.lower()))
            ],
        ),
        DataTest(
            name="processing item with url problem",
            item=TestItem({'url': 'example.com'}),
            settings={
                SETTING_MODELS: [TEST_VALIDATOR_PATH,],
            },
            cases="'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
        ),
        DataTest(
            name="processing nested items without errors",
            item=TreeItem({'child': TreeItem()}),
            settings={
                SETTING_MODELS: [TREE_VALIDATOR_PATH,],
            },
            cases=[
                "'{}' not in {{stats}}".format(STATS_ITEM_ERRORS),
                "{{stats}}['{}'] is 1".format(STATS_AMOUNTS),
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(UniversalItem.__name__.lower()))
            ],
        ),
        DataTest(
            name="missing required fields",
            item=TestItem(),
            settings={
                SETTING_MODELS: [TEST_VALIDATOR_PATH,],
            },
            cases="'{}' in {{stats}}".format(STATS_MISSINGS),
        ),
        DataTest(
            name="validator is {} type, validators in list repr".format(
                TestItem.__name__),
            item=TestItem(),
            settings={
                SETTING_MODELS: {
                    TestItem: [TEST_VALIDATOR_PATH],
                }
            },
            cases=[
                "'{}' in {{stats}}".format(STATS_ITEM_ERRORS),
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(TestItem.__name__.lower())),
            ],
        ),
        DataTest(
            name="support several schema validators per item",
            item=TestItem(),
            settings={
                SETTING_MODELS: {
                    TestItem: [
                        TEST_VALIDATOR_PATH,
                        TREE_VALIDATOR_PATH,
                    ],
                }
            },
            cases=[
                "{{stats}}['{}'] is 2".format(STATS_AMOUNTS),
                "{{stats}}['{}'] is 2".format(STATS_ITEM_ERRORS),
            ],
        ),
        DataTest(
            name="item of one type processed only by proper validator",
            item=TestItem({'url': 'http://example.com'}),
            settings={
                SETTING_MODELS: {
                    TestItem: TEST_VALIDATOR_PATH,
                    TreeItem: TREE_VALIDATOR_PATH,
                }
            },
            cases="'{}' not in {{stats}}".format(STATS_ITEM_ERRORS),
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
                "{{stats}}['{}'] is 1".format(STATS_MISSINGS),
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(TestItem.__name__.lower())),
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(TreeItem.__name__.lower())),
            ],
        ),
        DataTest(
            name="item should be processed by both validators",
            item=TestItem({'url': 'http://example.com'}),
            settings={
                SETTING_MODELS: {
                    TestItem: TEST_VALIDATOR_PATH,
                    UniversalItem: TREE_VALIDATOR_PATH,
                }
            },
            cases="'{}' in {{stats}}".format(STATS_MISSINGS),
        ),
    ]


class PipelineValidators(PipelineTest):

    data_tests = [
        DataTest(
            name="there are both validators per {} type".format(
                UniversalItem.__name__),
            item=TestItem(),
            settings={
                SETTING_SCHEMAS: [test_schema,],
                SETTING_MODELS: [TEST_VALIDATOR_PATH,],
            },
            cases=[
                "{{stats}}['{}'] is 2".format(STATS_AMOUNTS),
                "{{stats}}['{}'] is 2".format(STATS_ITEM_ERRORS),
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(UniversalItem.__name__.lower(), 'jsonschema')),
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(UniversalItem.__name__.lower(), 'schematics')),
            ],
        ),
        DataTest(
            name="proper validators handle only related items",
            item=TestItem({'url': 'http://example.com'}),
            settings={
                SETTING_SCHEMAS: {
                    TestItem: test_schema,
                    TreeItem: tree_schema,
                },
                SETTING_MODELS: {
                    UniversalItem: TEST_VALIDATOR_PATH,
                },
            },
            cases=[
                "{{stats}}['{}'] is 3".format(STATS_AMOUNTS),
                "'{}' not in {{stats}}".format(STATS_ITEM_ERRORS),
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(TestItem.__name__.lower(), 'jsonschema')),
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(TreeItem.__name__.lower(), 'jsonschema')),
                "'{}' in {{stats}}".format(
                    STATS_TYPES.format(UniversalItem.__name__.lower(), 'schematics')),
            ],
        ),
    ]

