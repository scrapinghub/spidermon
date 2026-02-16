import pytest

pytest.importorskip("scrapy")

import spidermon.contrib.validation.jsonschema.tools as schema_tools


def test_get_schema_from_url_fails(caplog, mocker):
    mocker.patch(
        "spidermon.contrib.validation.jsonschema.tools.get_contents",
        return_value={'"schema":'},
    )
    schema_tools.get_schema_from("https://something.org/schema.json")
    assert (
        "Could not parse schema from 'https://something.org/schema.json'"
        in caplog.record_tuples[0][2]
    )


def test_get_schema_from_file_fails(caplog, mocker):
    path = "tests/fixtures/bad_schema.json"
    schema_tools.get_schema_from(path)
    assert f"Could not parse schema in {path!r}" in caplog.record_tuples[0][2]


@pytest.mark.parametrize(
    "url, expected_result",
    [
        ("https://example.com", False),
        ("example.com/file.json", False),
        ("//bucket/file.json", False),
        ("https://example.com/file.json", True),
        ("s3://bucket/file.json", True),
    ],
)
def test_is_schema_url(url, expected_result):
    assert schema_tools.is_schema_url(url) == expected_result


def test_get_contents_fails(mocker, caplog):
    cm = mocker.MagicMock()
    cm.__enter__.return_value = cm
    cm.read.side_effect = ValueError("'ValueError' object has no attribute 'decode'")
    mocker.patch(
        "spidermon.contrib.validation.jsonschema.tools.urlopen",
        return_value=cm,
        autospec=True,
    )
    schema_tools.get_contents("https://example.com/schema.json")
    assert caplog.record_tuples == [
        (
            "spidermon.contrib.validation.jsonschema.tools",
            40,
            "'ValueError' object has no attribute 'decode'\nFailed to get 'https://example.com/schema.json'",
        ),
    ]
