from __future__ import absolute_import
from unittest import TestCase

from spidermon.contrib.validation import CerberusValidator
# from spidermon.contrib.validation import messages

from slugify import slugify
import six


class SchemaTestCaseMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        def _test_function(data_test):
            def _function(self):
                validator = CerberusValidator(data_test.schema or self.schema)
                assert validator.validate(data_test.data) == (
                    data_test.valid,
                    # data_test.expected_errors,
                )

            return _function

        cls = super(SchemaTestCaseMetaclass, mcs).__new__(mcs, name, bases, attrs)
        for dt in getattr(cls, "data_tests", []):
            function_name = "test_%s" % slugify(dt.name, separator="_").lower()
            setattr(cls, function_name, _test_function(dt))
        return cls


class SchemaTest(six.with_metaclass(SchemaTestCaseMetaclass, TestCase)):
    schema = {}
    data_tests = []


    # def test_schema(self):
    # What if the schema provided is not valid?
    # Return a message that dict is not valid, and stop.
        # pass

    def schema_exists():
        pass

    # def test_datadict(self):
    # What if the data provided is not valid (not a valid dict for example)?
        # self.assertIsInstance(getattr(DataTest(), data, []), dict, msg="Not a valid dict, please format the data properly in the form of a dict")
        # But what to do next.
        # pass


class DataTest(object):
    def __init__(self, name, data, valid, schema=None):
    # def __init__(self, name, data, schema=None, valid, expected_errors=None):
        self.name = name
        self.data = data
        self.valid = valid
        self.schema = schema
        # self.expected_errors = expected_errors

class Simple(SchemaTest):
    # error messages to be taken from translater
    schema={
        'number': {'type': 'integer'},
        'name': {'type': 'string'}
    },

    data_tests =[
        DataTest(
            name="Simple test Case",
            schema=schema,
            valid=True,
            data={"name": "foo","number": 5},
            # expected_errors={}
        ),
        DataTest(
            name="Simple case, invalid integer",
            schema=schema,
            valid=True,
            data={"name": "foo","number": "goo"},
            # expected_errors={"number":[messages.INVALID_INT]}
        ),
        DataTest(
            name="Simple case, invalid String",
            schema=schema,
            valid=True,
            data={"name": 1,"number": 2},
            # expected_errors={"name":[messages.INVALID_STRING]}
        ),
        DataTest(
            name="Simple case, unexpected field",
            schema=schema,
            valid=True,
            data={"name": "foo","number": 6, "price":30},
            # expected_errors={"price":[messages.UNEXPECTED_FIELD]}
        )
    ]

class Required(SchemaTest):
    schema = {"foo": {'required': True, 'type': 'string'}, 'bar': {'type': 'integer'}}
    schema_default = {"foo": {}}
    data_tests=[
        DataTest(
            name="Invalid case",
            schema=schema,
            data={"bar": 1},
            valid=False,
            # expected_errors={"foo": [messages.MISSING_REQUIRED_FIELD]},
        ),
        DataTest(
            name="Valid case",
            schema=schema,
            data={"foo":"toy"},
            valid=True,
        ),
        DataTest(
            name="not required by default", schema=schema_default, data={}, valid=True
        )
    ]
