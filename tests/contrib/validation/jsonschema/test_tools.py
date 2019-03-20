from spidermon.contrib.validation.jsonschema.tools import get_schema_from


def test_get_schema_from_url_fails(caplog, mocker):
    mocker.patch("spidermon.utils.web.get_contents", return_value={'"schema":'})
    get_schema_from("https://something.org/schema.json")
    assert (
        "Could not parse schema from 'https://something.org/schema.json'"
        in caplog.record_tuples[0][2]
    )


def test_get_schema_from_file_fails(caplog, mocker):
    path = "tests/fixtures/bad_schema.json"
    get_schema_from("tests/fixtures/bad_schema.json")
    assert (
        "Could not parse schema in 'tests/fixtures/bad_schema.json'"
        in caplog.record_tuples[0][2]
    )
