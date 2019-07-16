from __future__ import absolute_import
import pytest
from cerberus.validator import DocumentError, SchemaError
from spidermon.contrib.validation import CerberusValidator


@pytest.mark.parametrize(
    "data,schema",
    [
        pytest.param(
            {"name": "foo", "number": 5},
            {"name": {"typestring"}, "number": {"type": "integer"}},
            id="Schema Invalid",
        ),
        pytest.param(
            ["This is wrong"],
            {"name": {"type": "string"}, "number": {"type": "integer"}},
            id="Data invalid, not mapping type",
        ),
        pytest.param(
            ["foo"],
            {"name": {"x": "boo"}, "number": {"type": "integer"}},
            id="Both schema, and data invalid",
        ),
    ],
)
def test_raise_value_error_with_invalid_schemas(data, schema):
    validator = CerberusValidator(schema)
    with pytest.raises(ValueError):
        validator.validate(data)


@pytest.mark.parametrize(
    "data,schema", [pytest.param(None, {"name": {"type": "string"}}, id="Missing Data")]
)
def test_document_error_with_missing_data(data, schema):
    validator = CerberusValidator(schema)
    with pytest.raises(DocumentError):
        validator.validate(data)


@pytest.mark.parametrize(
    "data,schema",
    [pytest.param({"name": "foo", "number": 5}, None, id="Missing Schema")],
)
def test_schema_error_with_missing_schemas(data, schema):
    with pytest.raises(SchemaError):
        CerberusValidator(schema)


@pytest.mark.parametrize(
    "data,schema,valid,expected_errors",
    [
        pytest.param(
            {"name": "foo", "number": 5},
            {"name": {"type": "string"}, "number": {"type": "integer"}},
            True,
            {},
            id="Valid schema, data",
        )
    ],
)
def test_valid_schemas(data, schema, valid, expected_errors):
    validator = CerberusValidator(schema)
    assert validator.validate(data) == (valid, expected_errors)
