# -*- coding: utf-8 -*-
from unittest import TestCase

from spidermon.contrib.validation import JSONSchemaValidator
from spidermon.contrib.validation import messages

from slugify import slugify


class SchemaTestCaseMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        def _test_function(data_test):
            def _function(self):
                validator = JSONSchemaValidator(data_test.schema or self.schema)
                assert validator.validate(data_test.data) == (data_test.valid, data_test.expected_errors)
            return _function
        cls = super(SchemaTestCaseMetaclass, mcs).__new__(mcs, name, bases, attrs)
        for dt in getattr(cls, 'data_tests', []):
            function_name = 'test_%s' % slugify(dt.name, separator='_').lower()
            setattr(cls, function_name, _test_function(dt))
        return cls


class SchemaTest(TestCase):
    __metaclass__ = SchemaTestCaseMetaclass
    schema = {}
    data_tests = []


class DataTest(object):
    def __init__(self, name, data, valid, expected_errors=None, schema=None):
        self.name = name
        self.data = data
        self.valid = valid
        self.expected_errors = expected_errors or {}
        self.schema = schema


class Type(object):
#class Type(SchemaTest):
    type_tests = [
        # -------------------------------------------------------
        # type          data        expected error
        # -------------------------------------------------------
        # array
        ('array',       [],         None),
        ('array',       [1, 2],     None),
        ('array',       None,       messages.INVALID_ARRAY),
        ('array',       {},         messages.INVALID_ARRAY),
        ('array',       "[]",       messages.INVALID_ARRAY),
        ('array',       "abc",      messages.INVALID_ARRAY),
        ('array',       1,          messages.INVALID_ARRAY),

        # boolean
        ('boolean',     True,       None),
        ('boolean',     False,      None),
        ('boolean',     None,       messages.INVALID_BOOLEAN),
        ('boolean',     "True",     messages.INVALID_BOOLEAN),
        ('boolean',     "False",    messages.INVALID_BOOLEAN),
        ('boolean',     0,          messages.INVALID_BOOLEAN),
        ('boolean',     1,          messages.INVALID_BOOLEAN),

        # integer
        ('integer',     0,          None),
        ('integer',     1,          None),
        ('integer',     -500,       None),
        ('integer',     1000000,    None),
        ('integer',     None,       messages.INVALID_INT),
        ('integer',     1.2,        messages.INVALID_INT),
        ('integer',     "1",        messages.INVALID_INT),

        # number
        ('number',      0,          None),
        ('number',      1,          None),
        ('number',      -500,       None),
        ('number',      1000000,    None),
        ('number',      1.2,        None),
        ('number',      -34.7,      None),
        ('number',      None,       messages.INVALID_NUMBER),
        ('number',      "1",        messages.INVALID_NUMBER),
        ('number',      True,       messages.INVALID_NUMBER),

        # null
        ('null',        None,       None),
        ('null',        [],         messages.NOT_NULL),
        ('null',        {},         messages.NOT_NULL),
        ('null',        0,          messages.NOT_NULL),
        ('null',        "",         messages.NOT_NULL),

        # object
        ('object',      {},         None),
        ('object',      {'a': 1},   None),
        ('object',      None,       messages.INVALID_OBJECT),
        ('object',      [],         messages.INVALID_OBJECT),
        ('object',      0,          messages.INVALID_OBJECT),
        ('object',      "",         messages.INVALID_OBJECT),
        ('object',      "abc",      messages.INVALID_OBJECT),

        # string
        ('string',      "",         None),
        ('string',      "abc",      None),
        ('string',      "-",        None),
        ('string',      "...",      None),
        ('string',      u"",        None),
        ('string',      u"abc",     None),
        ('string',      u"España",  None),
        ('string',      "1",        None),
        ('string',      None,       messages.INVALID_STRING),
        ('string',      1,          messages.INVALID_STRING),
        ('string',      [],         messages.INVALID_STRING),
        ('string',      {},         messages.INVALID_STRING),
    ]
    data_tests = [
        DataTest(
            name='%02d_%s' % (i+1, data_type),
            data=data,
            valid=expected_error is None,
            expected_errors={'': [expected_error]} if expected_error else None,
            schema={"type": data_type},
        )
        for i, (data_type, data, expected_error) in enumerate(type_tests)
    ]


class AdditionalItems(object):
#class AdditionalItems(SchemaTest):
    data_tests = [
        DataTest(
            name="additionalItems as schema, additional items match schema",
            schema={
                "items": [{}],
                "additionalItems": {"type": "integer"},
            },
            data=[None, 2, 3, 4],
            valid=True,
        ),
        DataTest(
            name="additionalItems as schema, additional items do not match schema",
            schema={
                "items": [{}],
                "additionalItems": {"type": "integer"},
            },
            data=[None, 2, 3, "foo"],
            valid=False,
            expected_errors={
                '3': [messages.INVALID_INT],
            }
        ),
        DataTest(
            name="no additionalItems, all items match schema",
            schema={
                "items": {},
                "additionalItems": False
            },
            data=[1, 2, 3, 4, 5],
            valid=True
        ),
        DataTest(
            name="array of items with no additionalItems, no additional items present",
            schema={
                "items": [{}, {}, {}],
                "additionalItems": False
            },
            data=[1, 2, 3],
            valid=True
        ),
        DataTest(
            name="array of items with no additionalItems, additional items are not permitted",
            schema={
                "items": [{}, {}, {}],
                "additionalItems": False
            },
            data=[1, 2, 3, 4],
            valid=False,
            expected_errors={
                '': [messages.TOO_MANY_ITEMS],
            }
        ),
        DataTest(
            name="additionalItems as false without items, valid",
            schema={"additionalItems": False},
            data=[1, 2, 3, 4, 5],
            valid=True,
        ),
        DataTest(
            name="additionalItems as false without items, ignores non-arrays",
            schema={"additionalItems": False},
            data={"foo": "bar"},
            valid=True,
        ),
        DataTest(
            name="additionalItems are allowed by default, only the first item is validated",
            schema={"items": [{"type": "integer"}]},
            data=[1, "foo", False],
            valid=True,
        ),
        DataTest(
            name="array, sequence without extra item",
            schema={
                "type": "array",
                "items": [{"type": "boolean"}, {"type": "integer"}, {"type": "string"}],
                "additionalItems": {"type": "boolean"}
            },
            data=[True, 1, "foo"],
            valid=True,
        ),
        DataTest(
            name="array, sequence with valid extra item",
            schema={
                "type": "array",
                "items": [{"type": "boolean"}, {"type": "integer"}, {"type": "string"}],
                "additionalItems": {"type": "boolean"}
            },
            data=[True, 1, "foo", True],
            valid=True,
        ),
        DataTest(
            name="array, sequence with invalid extra item",
            schema={
                "type": "array",
                "items": [{"type": "boolean"}, {"type": "integer"}, {"type": "string"}],
                "additionalItems": {"type": "boolean"}
            },
            data=[True, 1, "foo", 1],
            valid=False,
            expected_errors={
                '3': [messages.INVALID_BOOLEAN],
            }
        ),
    ]


class AdditionalProperties(object):
#class AdditionalProperties(SchemaTest):
    schema_false = {
        "properties": {"foo": {}, "bar": {}},
        "patternProperties": {"^v": {}},
        "additionalProperties": False
    }
    schema_allows_schema = {
        "properties": {"foo": {}, "bar": {}},
        "additionalProperties": {"type": "boolean"}
    }
    schema_alone = {
        "additionalProperties": {"type": "boolean"}
    }
    schema_no = {
        "properties": {"foo": {}, "bar": {}}
    }
    data_tests = [
        DataTest(
            name="schema_false, no additional properties is valid",
            schema=schema_false,
            data={"foo": 1},
            valid=True,
        ),
        DataTest(
            name="schema_false, an additional property is invalid",
            schema=schema_false,
            data={"foo": 1, "bar": 2, "quux": "boom"},
            valid=False,
            expected_errors={
                '': [messages.UNEXPECTED_FIELD],
            }
        ),
        DataTest(
            name="schema_false, ignores non-objects",
            schema=schema_false,
            data=[1, 2, 3],
            valid=True,
        ),
        DataTest(
            name="schema_false, patternProperties are not additional properties",
            schema=schema_false,
            data={"foo": 1, "vroom": 2},
            valid=True,
        ),
        DataTest(
            name="schema_allows_schema, no additional properties",
            schema=schema_allows_schema,
            data={"foo": 1},
            valid=True,
        ),
        DataTest(
            name="schema_allows_schema, additional valid property",
            schema=schema_allows_schema,
            data={"foo": 1, "bar": 2, "quux" : True},
            valid=True,
        ),
        DataTest(
            name="schema_allows_schema, additional invalid property",
            schema=schema_allows_schema,
            data={"foo": 1, "bar": 2, "quux" : 12},
            valid=False,
            expected_errors={
                'quux': [messages.INVALID_BOOLEAN],
            }
        ),
        DataTest(
            name="schema_alone, additional valid property",
            schema=schema_alone,
            data={"foo": True},
            valid=True,
        ),
        DataTest(
            name="schema_alone, additional invalid property",
            schema=schema_alone,
            data={"foo": 1},
            valid=False,
            expected_errors={
                'foo': [messages.INVALID_BOOLEAN],
            }
        ),
        DataTest(
            name="schema_no, additional properties are allowed",
            schema=schema_no,
            data={"foo":1, "bar":2, "quux":True},
            valid=True,
        ),
    ]


class AllOf(object):
#class AllOf(SchemaTest):
    schema = {
        "type": "object",
        "properties": {
            "A": {"type": "boolean"},
            "B": {"type": "boolean"}
        },
        "allOf": [
            {"required": ["A"]},
            {"required": ["B"]}
        ]
    }
    data_tests = [
        DataTest(
            name="Empty object",
            data={},
            valid=False,
            expected_errors={
                'A': [messages.MISSING_REQUIRED_FIELD],
                'B': [messages.MISSING_REQUIRED_FIELD],
            }
        ),
        DataTest(
            name="Mismatch B",
            data={"A": True},
            valid=False,
            expected_errors={
                'B': [messages.MISSING_REQUIRED_FIELD],
            }
        ),
        DataTest(
            name="Mismatch A",
            data={"B": True},
            valid=False,
            expected_errors={
                'A': [messages.MISSING_REQUIRED_FIELD],
            }
        ),
        DataTest(
            name="Both values",
            data={"A": False, "B": False},
            valid=True,
        ),
        DataTest(
            name="Wrong type for A",
            data={"A": 1, "B": False},
            valid=False,
            expected_errors={
                'A': [messages.INVALID_BOOLEAN],
            }
        ),
        DataTest(
            name="Wrong type for both",
            data={"A": 1, "B": 1},
            valid=False,
            expected_errors={
                'A': [messages.INVALID_BOOLEAN],
                'B': [messages.INVALID_BOOLEAN],
            }
        ),
    ]


class AnyOf(object):
#class AnyOf(SchemaTest):
    schema = {
        "type": "object",
        "properties": {
            "A": {"type": "boolean"},
            "B": {"type": "boolean"}
        },
        "anyOf": [
            {"required": ["A"]},
            {"required": ["B"]}
        ]
    }
    data_tests = [
        DataTest(
            name="Empty object",
            data={},
            valid=False,
            expected_errors={
                '': [messages.NOT_VALID_UNDER_ANY_SCHEMA],
            }
        ),
        DataTest(
            name="Mismatch B",
            data={"A": True},
            valid=True,
        ),
        DataTest(
            name="Mismatch A",
            data={"B": True},
            valid=True,
        ),
        DataTest(
            name="Both values",
            data={"A": False, "B": False},
            valid=True,
        ),
        DataTest(
            name="Wrong type for A",
            data={"A": 1, "B": False},
            valid=False,
            expected_errors={
                'A': [messages.INVALID_BOOLEAN],
            }
        ),
        DataTest(
            name="Wrong type for both",
            data={"A": 1, "B": 1},
            valid=False,
            expected_errors={
                'A': [messages.INVALID_BOOLEAN],
                'B': [messages.INVALID_BOOLEAN],
            }
        ),
    ]


class OneOf(object):
#class OneOf(SchemaTest):
    schema = {
        "type": "object",
        "properties": {
            "A": {"type": "boolean"},
            "B": {"type": "boolean"}
        },
        "oneOf": [
            {"required": ["A"]},
            {"required": ["B"]}
        ]
    }
    data_tests = [
        DataTest(
            name="Empty object",
            data={},
            valid=False,
            expected_errors={
                '': [messages.NOT_VALID_UNDER_ANY_SCHEMA],
            }
        ),
        DataTest(
            name="Mismatch B",
            data={"A": True},
            valid=True,
        ),
        DataTest(
            name="Mismatch A",
            data={"B": True},
            valid=True,
        ),
        DataTest(
            name="Both values",
            data={"A": False, "B": False},
            valid=False,
            expected_errors={
                '': [messages.VALID_FOR_SEVERAL_EXCLUSIVE_SCHEMAS],
            }
        ),
        DataTest(
            name="Wrong type for A",
            data={"A": 1, "B": False},
            valid=False,
            expected_errors={
                '': [messages.VALID_FOR_SEVERAL_EXCLUSIVE_SCHEMAS],
                'A': [messages.INVALID_BOOLEAN],
            }
        ),
        DataTest(
            name="Wrong type for both",
            data={"A": 1, "B": 1},
            valid=False,
            expected_errors={
                '': [messages.VALID_FOR_SEVERAL_EXCLUSIVE_SCHEMAS],
                'A': [messages.INVALID_BOOLEAN],
                'B': [messages.INVALID_BOOLEAN],
            }
        ),
    ]


class Dependencies(object):
#class Dependencies(SchemaTest):
    schema_single = {
        "dependencies": {
            "bar": ["foo"],
        },
    }
    schema_multiple = {
        "dependencies": {
            "quux": ["foo", "bar"],
        },
    }
    schema_multiple_subschema = {
        "dependencies": {
            "bar": {
                "properties": {
                    "foo": {"type": "integer"},
                    "bar": {"type": "integer"},
                },
            },
        },
    }
    data_tests = [
        DataTest(
            name="single, neither",
            schema=schema_single,
            data={},
            valid=True,
        ),
        DataTest(
            name="single, nondependant",
            schema=schema_single,
            data={"foo": 1},
            valid=True,
        ),
        DataTest(
            name="single, with dependency",
            schema=schema_single,
            data={"foo": 1, "bar": 2},
            valid=True,
        ),
        DataTest(
            name="single, missing dependency",
            schema=schema_single,
            data={"bar": 2},
            valid=False,
            expected_errors={
                '': [messages.MISSING_DEPENDENT_FIELD],
            }
        ),
        DataTest(
            name="single, ignores non-objects",
            schema=schema_single,
            data="foo",
            valid=True,
        ),
        DataTest(
            name="multiple, neither",
            schema=schema_multiple,
            data={},
            valid=True,
        ),
        DataTest(
            name="multiple, nondependants",
            schema=schema_multiple,
            data={"foo": 1, "bar": 2},
            valid=True,
        ),
        DataTest(
            name="multiple, with dependencies",
            schema=schema_multiple,
            data={"foo": 1, "bar": 2, "quux": 3},
            valid=True,
        ),
        DataTest(
            name="multiple, missing dependency",
            schema=schema_multiple,
            data={"foo": 1, "quux": 2},
            valid=False,
            expected_errors={
                '': [messages.MISSING_DEPENDENT_FIELD],
            },
        ),
        DataTest(
            name="multiple, missing other dependency",
            schema=schema_multiple,
            data={"bar": 1, "quux": 2},
            valid=False,
            expected_errors={
                '': [messages.MISSING_DEPENDENT_FIELD],
            },
        ),
        DataTest(
            name="multiple, missing both dependencies",
            schema=schema_multiple,
            data={"quux": 1},
            valid=False,
            expected_errors={
                '': [messages.MISSING_DEPENDENT_FIELD, messages.MISSING_DEPENDENT_FIELD],
            },
        ),
        DataTest(
            name="multiple subschema, valid",
            schema=schema_multiple_subschema,
            data={"foo": 1, "bar": 2},
            valid=True,
        ),
        DataTest(
            name="multiple subschema, no dependency",
            schema=schema_multiple_subschema,
            data={"foo": "quux"},
            valid=True,
        ),
        DataTest(
            name="multiple subschema, wrong type",
            schema=schema_multiple_subschema,
            data={"foo": "quux", "bar": 2},
            valid=False,
            expected_errors={
                'foo': [messages.INVALID_INT],
            },
        ),
        DataTest(
            name="multiple subschema, wrong type other",
            schema=schema_multiple_subschema,
            data={"foo": 2, "bar": "quux"},
            valid=False,
            expected_errors={
                'bar': [messages.INVALID_INT],
            },
        ),
        DataTest(
            name="multiple subschema, wrong type both",
            schema=schema_multiple_subschema,
            data={"foo": "quux", "bar": "quux"},
            valid=False,
            expected_errors={
                'foo': [messages.INVALID_INT],
                'bar': [messages.INVALID_INT],
            },
        ),

    ]
