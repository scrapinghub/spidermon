import os
import sys

import pytest
from spidermon.contrib.validation.jsonschema.tools import get_schema_from


@pytest.mark.skipif(
    sys.version_info < (3, 5), reason="we don't want to test json on different versions"
)
def test_get_schema_from_url_fails(caplog, mocker):
    mocker.patch("spidermon.utils.web.get_contents", return_value={'"schema":'})
    get_schema_from("https://something.org/schema.json")
    assert caplog.record_tuples == [
        (
            "root",
            40,
            (
                "the JSON object must be str, bytes or bytearray, not set\n"
                "Could not parse schema from 'https://something.org/schema.json'"
            ),
        )
    ]


@pytest.mark.skipif(
    sys.version_info < (3, 5), reason="we don't want to test json on different versions"
)
def test_get_schema_from_file_fails(caplog, mocker):
    path = "tests/fixtures/bad_schema.json"
    get_schema_from("tests/fixtures/bad_schema.json")
    assert caplog.record_tuples == [
        (
            "root",
            40,
            (
                "Expecting ',' delimiter: line 14 column 6 (char 260)\n"
                "Could not parse schema in 'tests/fixtures/bad_schema.json'"
            ),
        )
    ]
