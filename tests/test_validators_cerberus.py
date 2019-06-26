from __future__ import absolute_import
from unittest import TestCase

from spidermon.contrib.validation import CerberusValidator
from spidermon.contrib.validation import messages

class TestCerberusValidator(TestCase):
    def test_schema(self):
    # What if the schema provided is not valid?
    # Return a message that dict is not valid, and stop.
        pass

    def test_datadict(self):
    # What if the data provided is not valid (not a valid dict for example)?
        self.assertIsInstance(getattr(DataTest(), data, []), dict, msg="Not a valid dict, please format the data properly in the form of a dict")
        # But what to do next.

    def test_data():
         # Assert Validate method to check with Cerberus
        pass

class DataTest(object):
    def __init__(self, name, data, valid, schema=None):
    # def __init__(self, name, data, schema=None, valid, errors=None):
        self.name = name
        self.data = data
        self.valid = valid
        self.schema = schema
        # self.errors = errors

class Testing_center(TestCerberusValidator):
    # error messages to be taken from translater
    schema={
        'number': {'type': 'integer'},
        'name': {'type': 'string'}
    },

    DataTest(
        name="Simple Case",
        schema=schema,
        valid=True,
        data={"name": "foo","number": 5},
    )
    DataTest(
        name="Simple case, invalid integer",
        schema=schema,
        valid=True,
        data={"name": "foo","number": "goo"},
        errors={"number":[messages.INVALID_INT]}
    )
    DataTest(
        name="Simple case, invalid String",
        schema=schema,
        valid=True,
        data={"name": 1,"number": 2},
        errors={"name":[messages.INVALID_STRING]}
    )
    DataTest(
        name="Simple case, unexpected field",
        schema=schema,
        valid=True,
        data={"name": "foo","number": 6, "price":30},
        errors={"price":[messages.UNEXPECTED_FIELD]}
    )
