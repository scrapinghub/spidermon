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


#class AnyOf(SchemaTest):
class AnyOf(object):
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
