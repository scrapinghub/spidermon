import pytest
from spidermon.utils import web


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
