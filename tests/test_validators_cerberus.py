from __future__ import absolute_import
import pytest

from spidermon.contrib.validation import CerberusValidator
from spidermon.contrib.validation import CerberusMessageTranslator
from spidermon.contrib.validation import messages


@pytest.mark.parametrize(
    "error,message",
    [
        pytest.param(
            "required field",
            messages.MISSING_REQUIRED_FIELD,
            id="Message of REQUIRED Field",
        ),
        pytest.param(
            "empty values not allowed",
            messages.EMPTY_NOT_ALLOWED,
            id="Message of Empty Value",
        ),
        pytest.param(
            "Unknown field",
            messages.UNKNOWN_FIELD,
            id="Message of Unknown field is present",
        ),
        pytest.param(
            "null value not allowed",
            messages.NULL_NOT_ALLOWED,
            id="Message when NULL value is present",
        ),
        pytest.param(
            "value does not match regex '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+$'",
            messages.REGEX_NOT_MATCHED,
            id="Message of when REGEX NOT MATCHED",
        ),
    ],
)
def test_cerberus_translator_valid_messages(error, message):
    translator = CerberusMessageTranslator()
    assert translator.translate_message(error) == (message)


@pytest.mark.parametrize(
    "error,message",
    [
        pytest.param(
            "value does not match regex '^[a-z]*$'",
            messages.MISSING_DEPENDENT_FIELD,
            id="Invalid message for REGEX NOT MATCHED error",
        ),
        pytest.param(
            "Unknown field",
            messages.UNEXPECTED_FIELD,
            id="Invalid error of UNEXPECTED FIELD",
        ),
    ],
)
def test_cerberus_translator_invalid_messages(error, message):
    translator = CerberusMessageTranslator()
    with pytest.raises(AssertionError):
        assert translator.translate_message(error) == (message)


@pytest.mark.parametrize(
    "schema,data,valid,expected_errors",
    [
        pytest.param(
            {"foo": {"nullable": False, "type": "string"}, "bar": {"type": "integer"}},
            {"foo": None},
            False,
            {"foo": [messages.NULL_NOT_ALLOWED]},
            id="Nullable - Invalid case",
        ),
        pytest.param(
            {"foo": {"required": True, "type": ["binary", "list"]}},
            {"foo": [101, 1111111]},
            True,
            {},
            id="Binary, multiple types - Valid case",
        ),
        # This wouldn't work out, help needed here  --> Output (message = {0: ['must be of string type']) causing typeError
        # pytest.param(
        #     {'quotes': {'type': ['string', 'list'], 'schema': {'type': 'string'}}},
        #     {'quotes': [1, 'Heureka!']},
        #     False,
        #     {"foo": [messages.INVALID_STRING]},
        #     id="Multiple Types - Invalid Case",
        # ),
        pytest.param(
            {
                "foo": {
                    "type": "dict",
                    "schema": {
                        "address": {"type": "string"},
                        "city": {"type": "string", "required": True},
                    },
                },
                "1": {"empty": False, "type": "string"},
            },
            {"foo": {"address": "my address", "city": "my town"}, "1": ""},
            False,
            {"1": [messages.EMPTY_NOT_ALLOWED]},
            id="Empty values - Invalid Case",
        ),
    ],
)
def test_required_rule(schema, data, valid, expected_errors):
    validator = CerberusValidator(schema)
    assert validator.validate(data) == (valid, expected_errors)
