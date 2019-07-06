from __future__ import absolute_import
import pytest

from spidermon.contrib.validation import CerberusValidator
from spidermon.contrib.validation import messages

# Format for parameters
# 1. schema
# 2. data
# 3. valid
# 4. expected_errors
# 5. Id of test

# Format of test
# @pytest.mark.parametrize(
#     "schema,data,valid,expected_errors",
#     [
        # pytest.param(
        #     schema,
        #     data,
        #     valid,
        #     expected,
        #     id=
        # )
#     ],
# )
# def test_required_rule(schema, data, valid, expected_errors):
#     validator = CerberusValidator(schema)
#     assert validator.validate(data) == (valid, expected_errors)


@pytest.mark.parametrize(
    "schema,data,valid,expected_errors",
    [
        pytest.param(
            {"foo": {"required": True, "type": "string"}, "bar": {"type": "integer"}},
            {"bar": 1},
            False,
            {"foo": [messages.MISSING_REQUIRED_FIELD]},
            id="REQUIRED - Invalid case",
        ),
        pytest.param(
            {"foo": {"required": True, "type": "string"}, "bar": {"type": "integer"}},
            {"foo": "toy"},
            True,
            {},
            id="REQUIRED - Valid case"
        ),
        pytest.param(
            {"foo": {}},
            {},
            True,
            {},
            id="NOT REQUIRED - by default"
        )
    ]
)
def test_required_rule(schema, data, valid, expected_errors):
    validator = CerberusValidator(schema)
    assert validator.validate(data) == (valid, expected_errors)


# class Pattern(SchemaTest):
#     schema = {
#         'email': {
#             'type': 'string',
#             'regex': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
#         }
#     }
#     schema_default = {'word': {'type': 'string', 'regex': '^a*$'} }
#     data_tests = [
#         DataTest(
#             name="Invalid_email_case",
#             data={'email': 'john_at_example_dot_com'},
#             schema=schema,
#             valid=False,
#             expected_errors = {"email": [messages.REGEX_NOT_MATCHED]},
#         ),
#         DataTest(
#             name="Valid email case",
#             data={'email': 'john@example.com'},
#             schema= schema,
#             valid= True,
#             expected_errors={}
#         ),
#         DataTest(
#             name="valid",
#             schema=schema_default,
#             data={"word": "aaa"},
#             valid=True,
#             expected_errors={}
#         ),
#         DataTest(
#             name="invalid",
#             data={"word": "abc"},
#             schema=schema_default,
#             valid=False,
#             expected_errors={"word": [messages.REGEX_NOT_MATCHED]},
#         ),
#         # This doesn't work with Cerberus, need to confirm
#         # DataTest(
#         #     name="ignores non-strings",
#         #     schema=schema_default,
#         #     data={"word": True},
#         #     valid=True,
#         #     expected_errors={}
#         # ),
#     ]


# class Allowed(SchemaTest):
#     schema = {'role': {'type': 'list', 'allowed': ['agent', 'client', 'supplier']}}
#     data_tests = [
#         DataTest(
#             name="Allowed - valid case, both valid",
#             schema=schema,
#             data={'role': ['agent','client']},
#             valid=True,
#             expected_errors={},
#         ),
#         DataTest(
#             name="Allowed - invalid case, invalid",
#             schema=schema,
#             data={'role': ['intern']},
#             valid=False,
#             expected_errors={"role":[messages.NOT_ALLOWED_VALUE]},
#         ),
#         DataTest(
#             name="Allowed - invalid case, 1 invalid 1 valid",
#             schema=schema,
#             data={'role': ['CEO', 'supplier']},
#             valid=False,
#             expected_errors={"role":[messages.NOT_ALLOWED_VALUE]},
#         )
#     ]

# Should we also keep allow_unknown=True
# class Allow_Unknown(SchemaTest):

# class Unknown(SchemaTest):
#     schema = {
#         'items': {'type':'integer'}, 'age':{'type':'string'}
#     }
#     data_tests = [
#         DataTest(
#             name="One unexpected field",
#             schema=schema,
#             valid=False,
#             data={"name": 1, "items": 2},
#             expected_errors={"name":[messages.UNEXPECTED_FIELD]}
#         ),
#         DataTest(
#             name="No unexpected fields",
#             schema=schema,
#             valid=True,
#             data={"age": "Forty", "items": 2},
#             expected_errors={}
#         ),
#         DataTest(
#             name="2 or more unexpected fields",
#             schema=schema,
#             valid=False,
#             data={"name": 1, "sex": True},
#             expected_errors={
#                 "name": [messages.UNEXPECTED_FIELD],
#                 'age': [messages.UNEXPECTED_FIELD]
#             }
#         ),
#     ]

# class MinLength(SchemaTest):
#     schema = {}
#     data_tests=[
#         DataTest(
#             name="One unexpected field",
#             schema=schema,
#             valid=False,
#             data={"name": 1, "items": 2},
#             expected_errors={"name":[messages.UNEXPECTED_FIELD]}
#         ),
#     ]


# Class maxlength


# class Simple(SchemaTest):
#     # error messages to be taken from translater
#     schema = ({"number": {"type": "integer"}, "name": {"type": "string"}},)

#     data_tests = [
#         DataTest(
#             name="Simple test Case",
#             schema=schema,
#             valid=True,
#             data={"name": "foo", "number": 5},
#             # expected_errors={}
#         ),
#         DataTest(
#             name="Simple case, invalid integer",
#             schema=schema,
#             valid=False,
#             data={"name": "foo", "number": "goo"},
#             # expected_errors={"number":[messages.INVALID_INT]}
#         ),
# DataTest(
#     name="Simple case, invalid String",
#     schema=schema,
#     valid=False,
#     data={"name": 1, "number": 2},
#     # expected_errors={"name":[messages.INVALID_STRING]}
# ),
#         DataTest(
#             name="Simple case, unexpected field",
#             schema=schema,
#             valid=False,
#             data={"name": "foo", "number": 6, "price": 30},
#             # expected_errors={"price":[messages.UNEXPECTED_FIELD]}
#         ),
#     ]


# class AnyOf(SchemaTest):
#     schema = {
#         'A': {'type': 'boolean','anyOf': [{'required': ['A']}, {'required': ['B']}]
#     }}
#     data_tests = [
#         DataTest(
#             name='Empty object',
#             data={},
#             valid=False,
#             # expected_errors={'': [messages.NOT_VALID_UNDER_ANY_SCHEMA]},
#         ),
#         DataTest(name='Mismatch B', data={'A': True}, valid=True),
#         DataTest(name='Mismatch A', data={'B': True}, valid=True),
#         DataTest(name='Both values', data={'A': False, 'B': False}, valid=True),
#         DataTest(
#             name='Wrong type for A',
#             data={'A': 1, 'B': False},
#             valid=False,
#             # expected_errors={'A': [messages.INVALID_BOOLEAN]},
#         ),
#         DataTest(
#             name='Wrong type for both',
#             data={'A': 1, 'B': 1},
#             valid=False,
#             # expected_errors={
#             #     'A': [messages.INVALID_BOOLEAN],
#             #     'B': [messages.INVALID_BOOLEAN],
#             # },
#         ),
#     ]


# class AllOf(SchemaTest):
#     schema = {
#         'A': {'type': 'float', 'allof': [{'min':100.0, 'max':101.0}, {'min':0.0, 'max':1.0}]},
#         'B': {'type': 'integer', 'allof': [{'min':40, 'max':50}, {'min':70, 'max':80}]}
#     }

#     data_tests = [
#         DataTest(
#             name="Empty object",
#             data={},
#             valid=False,
#             # expected_errors={
#             #     "A": [messages.MISSING_REQUIRED_FIELD],
#             #     "B": [messages.MISSING_REQUIRED_FIELD],
#             # },
#         ),
#         DataTest(
#             name="Mismatch B",
#             data={"A": 9},
#             valid=False,
#             # expected_errors={"B": [messages.MISSING_REQUIRED_FIELD]},
#         ),
#         DataTest(
#             name="Mismatch A",
#             data={"B": 55},
#             valid=False,
#             # expected_errors={"A": [messages.MISSING_REQUIRED_FIELD]},
#         ),
#         DataTest(name="Both values", data={"A": , "B": False}, valid=True),
#         DataTest(
#             name="Wrong type for A",
#             data={"A": 1, "B": False},
#             valid=False,
#             # expected_errors={"A": [messages.INVALID_BOOLEAN]},
#         ),
#         DataTest(
#             name="Wrong type for both",
#             data={"A": 1, "B": 1},
#             valid=False,
#             # expected_errors={
#             #     "A": [messages.INVALID_BOOLEAN],
#             #     "B": [messages.INVALID_BOOLEAN],
#             # },
#         ),
#     ]
