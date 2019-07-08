from __future__ import absolute_import
import pytest

from spidermon.contrib.validation import CerberusValidator
from spidermon.contrib.validation import messages

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
