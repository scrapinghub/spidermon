import pytest

from spidermon.contrib.validation import messages


def test_unexpected_fields_deprecated():
    with pytest.warns(DeprecationWarning, match="UNEXPECTED_FIELDS is deprecated"):
        assert messages.UNEXPECTED_FIELDS == "Unexpected fields: {unexpected_fields}"


def test_unknown_attribute():
    with pytest.raises(AttributeError):
        messages.DOES_NOT_EXIST  # noqa: B018
