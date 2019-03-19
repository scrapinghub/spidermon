import pytest
from spidermon.utils import web
from six.moves.urllib.error import HTTPError
import logging


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
    assert web.is_schema_url(url) == expected_result


def test_get_contents_fails(mocker, caplog):
    cm = mocker.MagicMock()
    cm.__enter__.return_value = cm
    cm.read.side_effect = ValueError("'ValueError' object has no attribute 'decode'")
    mocked_urlopen = mocker.patch(
        "spidermon.utils.web.urlopen", return_value=cm, autospec=True
    )
    web.get_contents("https://example.com/schema.json")
    assert caplog.record_tuples == [
        (
            "root",
            40,
            "'ValueError' object has no attribute 'decode'\nFailed to get 'https://example.com/schema.json'",
        )
    ]
