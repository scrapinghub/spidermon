from __future__ import absolute_import
from unittest import TestCase

from spidermon.contrib.validation import CerberusValidator

# from spidermon.contrib.validation import messages

from slugify import slugify
import six


class SchemaTestCaseMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        def _test_function(data_test):
            def test_schema():
                self.assertIsInstance(data_test.schema, dict, msg="Not a valid dict, please format the schema properly")
                return

            def test_datadict(self):
                self.assertIsInstance(
                    data_test.data, dict, msg="Not a valid dict, please format the data properly in the form of a dict",
                )
                return

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



class DataTest(object):
    def __init__(self, name, data, valid, schema=None):
        # def __init__(self, name, data, schema=None, valid, expected_errors=None):
        self.name = name
        self.data = data
        self.valid = valid
        self.schema = schema
        # self.expected_errors = expected_errors

class Required(SchemaTest):
    schema = {"foo": {"required": True, "type": "string"}, "bar": {"type": "integer"}}
    schema_default = {"foo": {}}
    data_tests = [
        DataTest(
            name="Invalid case",
            schema=schema,
            data={"bar": 1},
            valid=False,
            # expected_errors={"foo": [messages.MISSING_REQUIRED_FIELD]},
        ),
        DataTest(name="Valid case", schema=schema, data={"foo": "toy"}, valid=True),
        DataTest(
            name="not required by default", schema=schema_default, data={}, valid=True
        ),
    ]

class Pattern(SchemaTest):
    schema = {
        'email': {'type': 'string',
        'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'}
    }
    schema_default = {'word': {'type': 'string', 'regex': '^a*$'} }
    data_tests = [
        DataTest(
            name="Invalid_email_case"
            data={'email': 'john_at_example_dot_com'},
            schema=schema,
            valid=False,
            # expected_errors = messages.REGEX_NOT_MATCHED]},
        },

        DataTest(
            name="Valid email case"
            data={'email': 'john@example.com'},
            schema= schema',
            valid= True,

        DataTest(name="valid", schema=schema_default data="aaa", valid=True),
        DataTest(
            name="invalid",
            data="abc",
            valid=False,
            expected_errors={"": [messages.REGEX_NOT_MATCHED]},
        ),
        DataTest(name="ignores non-strings", schema=schema_default, data=True, valid=True),
    ]
