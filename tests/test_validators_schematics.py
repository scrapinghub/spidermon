from __future__ import absolute_import
import schematics
from schematics.exceptions import ValidationError
from schematics.models import Model
from schematics.types import (
    StringType,
    DateTimeType,
    DateType,
    FloatType,
    IntType,
    LongType,
    DecimalType,
    BooleanType,
    EmailType,
    URLType,
    UUIDType,
    IPv4Type,
    MD5Type,
    SHA1Type,
)
from schematics.types.compound import ListType, DictType, ModelType

from spidermon.contrib.validation import SchematicsValidator, messages


SCHEMATICS1 = schematics.__version__.startswith("1.")


def test_rogue_fields():
    """
    messages:
        - UNEXPECTED_FIELD
    """
    _test_data(
        model=Model, data={"a": 1}, expected=(False, {"a": [messages.UNEXPECTED_FIELD]})
    )
    _test_data(model=Model, data={"a": 1}, expected=(True, {}), strict=False)


def test_required():
    """
    messages:
        - MISSING_REQUIRED_FIELD
    """

    class DataRequired(Model):
        a = StringType(required=True)

    class DataNotRequired(Model):
        a = StringType(required=False)

    _test_data(
        model=DataRequired,
        data={},
        expected=(False, {"a": [messages.MISSING_REQUIRED_FIELD]}),
    )
    _test_data(model=DataNotRequired, data={}, expected=(True, {}))


def test_choices():
    """
    messages:
        - VALUE_NOT_IN_CHOICES
    """

    class Data(Model):
        a = StringType(choices=["a", "b"])
        b = IntType(choices=[1, 2, 3])

    _test_data(model=Data, data={}, expected=(True, {}))
    _test_data(model=Data, data={"a": "b", "b": 3}, expected=(True, {}))
    _test_data(
        model=Data,
        data={"a": "c", "b": 4},
        expected=(
            False,
            {
                "a": [messages.VALUE_NOT_IN_CHOICES],
                "b": [messages.VALUE_NOT_IN_CHOICES],
            },
        ),
    )


def test_string_valid():
    """
    messages:
        - INVALID_STRING
    """

    class Data(Model):
        a = StringType()

    _test_data(model=Data, data={"a": "hello there!"}, expected=(True, {}))
    _test_data(
        model=Data, data={"a": []}, expected=(False, {"a": [messages.INVALID_STRING]})
    )


def test_string_lengths():
    """
    messages:
        - FIELD_TOO_SHORT
        - FIELD_TOO_LONG
    """

    class Data(Model):
        a = StringType(min_length=2, max_length=5)

    _test_data(model=Data, data={"a": "12"}, expected=(True, {}))
    _test_data(model=Data, data={"a": "12345"}, expected=(True, {}))
    _test_data(
        model=Data, data={"a": "1"}, expected=(False, {"a": [messages.FIELD_TOO_SHORT]})
    )
    _test_data(
        model=Data,
        data={"a": "123456"},
        expected=(False, {"a": [messages.FIELD_TOO_LONG]}),
    )


def test_string_regex():
    """
    messages:
        - REGEX_NOT_MATCHED
    """

    class Data(Model):
        a = StringType(regex=".*def.*")

    _test_data(
        model=Data,
        data={"a": "abc"},
        expected=(False, {"a": [messages.REGEX_NOT_MATCHED]}),
    )
    _test_data(model=Data, data={"a": "abcdefghi"}, expected=(True, {}))
    _test_data(model=Data, data={"a": "def"}, expected=(True, {}))


def test_datetime():
    """
    messages:
        - INVALID_DATETIME
    """

    class Data(Model):
        a = DateTimeType()

    class DataWithFormats(Model):
        a = DateTimeType(formats=("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"))

    if SCHEMATICS1:
        INVALID = ["2015-05-13 13:35:15.718978", "2015-05-13 13:35:15"]
    else:
        INVALID = ["foo", "1-2-3"]
        CUSTOM_FORMAT = ["2015-05-13 13:35:15.718978", "2015-05-13 13:35:15"]
    VALID = ["2015-05-13T13:35:15.718978", "2015-05-13T13:35:15"]
    _test_valid_invalid(
        model=Data,
        valid=VALID,
        invalid=INVALID,
        expected_error=messages.INVALID_DATETIME,
    )
    if SCHEMATICS1:
        for dt in INVALID:
            _test_data(model=DataWithFormats, data={"a": dt}, expected=(True, {}))
    else:
        for dt in CUSTOM_FORMAT:
            _test_data(model=DataWithFormats, data={"a": dt}, expected=(True, {}))


def test_date():
    """
    messages:
        - INVALID_DATE
    """

    class Data(Model):
        a = DateType()

    INVALID = ["2015-05-13 13:35:15", "13-05-2013", "2015-20-13", "2015-01-40"]
    VALID = ["2015-05-13", "2050-01-01"]
    _test_valid_invalid(
        model=Data, valid=VALID, invalid=INVALID, expected_error=messages.INVALID_DATE
    )


def test_int():
    """
    messages:
        - INVALID_INT
        - NUMBER_TOO_LOW
        - NUMBER_TOO_HIGH
    """

    class Data(Model):
        a = IntType(min_value=-10, max_value=10)
        b = IntType()

    INVALID = ["", "a", "2a", "2015-05-13 13:35:15", "7.2"]
    VALID = ["1", "8", "-2", "-7", 1, 8, -2, -7]
    if SCHEMATICS1:
        VALID.append(7.2)
    else:
        INVALID.append(7.2)
    _test_valid_invalid(
        model=Data, valid=VALID, invalid=INVALID, expected_error=messages.INVALID_INT
    )
    _test_data(
        model=Data, data={"a": -20}, expected=(False, {"a": [messages.NUMBER_TOO_LOW]})
    )
    _test_data(
        model=Data, data={"a": 11}, expected=(False, {"a": [messages.NUMBER_TOO_HIGH]})
    )


def test_float():
    """
    messages:
        - INVALID_FLOAT
        - NUMBER_TOO_LOW
        - NUMBER_TOO_HIGH
    """

    class Data(Model):
        a = FloatType(min_value=-10, max_value=10)

    INVALID = ["", "a", "2a", "2015-05-13 13:35:15"]
    VALID = [
        "1",
        "-2",
        "8",
        "2.3",
        "5.2354958",
        "-9.231",
        1,
        -2,
        8,
        2.3,
        5.2354958,
        -9.231,
    ]
    _test_valid_invalid(
        model=Data, valid=VALID, invalid=INVALID, expected_error=messages.INVALID_FLOAT
    )
    _test_data(
        model=Data, data={"a": -20}, expected=(False, {"a": [messages.NUMBER_TOO_LOW]})
    )
    _test_data(
        model=Data, data={"a": 11}, expected=(False, {"a": [messages.NUMBER_TOO_HIGH]})
    )


def test_long():
    """
    messages:
        - INVALID_LONG
        - NUMBER_TOO_LOW
        - NUMBER_TOO_HIGH
    """

    class Data(Model):
        a = LongType(min_value=-10, max_value=10)

    INVALID = ["", "a", "2a", "2015-05-13 13:35:15", "2.3", "5.2354958"]
    VALID = ["1", "-2", "8", 1, -2, 8]
    if SCHEMATICS1:
        expected_error = messages.INVALID_LONG
    else:
        expected_error = messages.INVALID_INT
    _test_valid_invalid(
        model=Data, valid=VALID, invalid=INVALID, expected_error=expected_error
    )
    _test_data(
        model=Data, data={"a": -20}, expected=(False, {"a": [messages.NUMBER_TOO_LOW]})
    )
    _test_data(
        model=Data, data={"a": 11}, expected=(False, {"a": [messages.NUMBER_TOO_HIGH]})
    )


def test_decimal():
    """
    messages:
        - INVALID_DECIMAL
        - NUMBER_TOO_LOW
        - NUMBER_TOO_HIGH
    """

    class Data(Model):
        a = DecimalType(min_value=-10, max_value=10)

    INVALID = ["", "a", "2a", "2015-05-13 13:35:15"]
    VALID = [
        "1",
        "-2",
        "8",
        "2.3",
        "5.2354958",
        "-9.231",
        1,
        -2,
        8,
        2.3,
        5.2354958,
        -9.231,
    ]
    _test_valid_invalid(
        model=Data,
        valid=VALID,
        invalid=INVALID,
        expected_error=messages.INVALID_DECIMAL,
    )
    _test_data(
        model=Data, data={"a": -20}, expected=(False, {"a": [messages.NUMBER_TOO_LOW]})
    )
    _test_data(
        model=Data, data={"a": 11}, expected=(False, {"a": [messages.NUMBER_TOO_HIGH]})
    )


def test_boolean():
    """
    messages:
        - INVALID_BOOLEAN
        - NUMBER_TOO_LOW
        - NUMBER_TOO_HIGH
    """

    class Data(Model):
        a = BooleanType()

    INVALID = ["", "a", "2" "TRUE", "FALSE", "TruE", "FalsE"]
    VALID = [0, 1, "0", "1", "True", "False", "true", "false", True, False]
    _test_valid_invalid(
        model=Data,
        valid=VALID,
        invalid=INVALID,
        expected_error=messages.INVALID_BOOLEAN,
    )


def test_email():
    """
    messages:
        - INVALID_EMAIL
        - NUMBER_TOO_LOW
        - NUMBER_TOO_HIGH
    """

    class Data(Model):
        a = EmailType()

    INVALID = [
        "",
        "johndoe",
        "johndoe@domain" "johndoe@domain." "@domain" "@domain.com" "domain.com",
    ]
    VALID = [
        "johndoe@domain.com",
        "john.doe@domain.com",
        "john.doe@sub.domain.com",
        "j@sub.domain.com",
        "j@d.com",
        "j@domain.co.uk",
    ]
    _test_valid_invalid(
        model=Data, valid=VALID, invalid=INVALID, expected_error=messages.INVALID_EMAIL
    )


def test_url():
    """
    messages:
        - INVALID_URL
    """

    class Data(Model):
        a = URLType()

    INVALID = [
        "",
        "http://",
        "http://www.",
        "www.",
        "http://www. .com",
        "domain.com",
        "www.domain.com",
        "http:/www.domain.com",
        "http//www.domain.com",
        "http:www.domain.com",
        "htp://domain.com/",
        "http://sub.domain.com\\en-us\\default.aspx\\",
        "http:\\\\msdn.domain.com\\en-us\\library\\default.aspx\\",
        "http:\\\\www.domain.com\\leafnode-L1.html",
        "./",
        "../",
        "http:\\\\www.domain.com\\leafnode-L1.xhtml\\",
    ]
    VALID = [
        "http://www.domain",
        "http://www.com",
        "http://www.domain.com.",
        "http://www.domain.com/.",
        "http://www.domain.com/..",
        "http://www.domain.com//cataglog//index.html",
        "http://www.domain.net/",
        "http://www.domain.com/level2/leafnode-L2.xhtml/",
        "http://www.domain.com/level2/level3/leafnode-L3.xhtml/",
        "http://www.domain.com?pageid=123&testid=1524",
        "http://www.domain.com/do.html#A",
    ]
    _test_valid_invalid(
        model=Data, valid=VALID, invalid=INVALID, expected_error=messages.INVALID_URL
    )


def test_uuid():
    """
    messages:
        - INVALID_UUID
    """

    class Data(Model):
        a = UUIDType()

    INVALID = [
        "",
        "678as6sd88ads67",
        "678as6sd88ads67-alskjlasd",
        "xxxxxxxx-xxxx-Mxxx-Nxxx-xxxxxxxxxxxx",
        "2.25.290383009913173870543740933812899923227",
    ]
    VALID = [
        "12345678-1234-5678-1234-567812345678",
        "12345678123456781234567812345678",
        "urn:uuid:12345678-1234-5678-1234-567812345678",
        "cfc63f3f-f3a7-465a-8183-acf055c6d472",
        "00000000-0000-0000-0000-000000000000",
        "01234567-89ab-cdef-0123456789abcdef",
        "0123456789abcdef0123456789abcdef",
    ]
    _test_valid_invalid(
        model=Data, valid=VALID, invalid=INVALID, expected_error=messages.INVALID_UUID
    )


def test_ipv4type():
    """
    messages:
        - INVALID_IPV4
    """

    class Data(Model):
        a = IPv4Type()

    INVALID = [
        "",
        "0",
        "0.",
        "0.0",
        "0.0.",
        "0.0.0",
        "0.0.0.0.",
        "0.0.0.0.0",
        "256.256.256.256",
        "2002:4559:1FE2::4559:1FE2",
        "2002:4559:1FE2:0:0:0:4559:1FE2",
        "2002:4559:1FE2:0000:0000:0000:4559:1FE2",
    ]
    VALID = [
        "98.139.180.149",
        "69.89.31.226",
        "192.168.1.1",
        "127.0.0.0",
        "0.0.0.0",
        "255.255.255.255",
    ]
    _test_valid_invalid(
        model=Data, valid=VALID, invalid=INVALID, expected_error=messages.INVALID_IPV4
    )


def test_md5():
    """
    messages:
        - INVALID_HASH
        - INVALID_HASH_LENGTH
    """

    class Data(Model):
        a = MD5Type()

    INVALID = [
        "_b1a9953c4611296a827abf8a47804d7",
        "zb1a9953c4611296a827abf8a47804d7",
        "Gb1a9953c4611296a827abf8a47804d7",
        # FIXME: PY3: schematics uses integer conversion for validating hex and
        # Py3 integers can contain underscores.
        # '8b1_9953c4611296a827abf8c47804d1',
    ]
    VALID = [
        "8b1a9953c4611296a827abf8c47804d7",
        "7dd4bbe8a38600b556f79ca44c9b5132",
        "11111111111111111111111111111111",
        "8B1A9953C4611296A827ABF8C47804D1",
    ]
    _test_valid_invalid(
        model=Data, valid=VALID, invalid=INVALID, expected_error=messages.INVALID_HASH
    )
    _test_data(
        model=Data,
        data={"a": "8b1a9953c4611296a827abf8c47804d"},
        expected=(False, {"a": [messages.INVALID_HASH_LENGTH]}),
    )
    _test_data(
        model=Data,
        data={"a": "8b1a9953c4611296"},
        expected=(False, {"a": [messages.INVALID_HASH_LENGTH]}),
    )
    _test_data(
        model=Data,
        data={"a": "8b1a9953c46112968b1a9953c46112968b1a9953c4611296"},
        expected=(False, {"a": [messages.INVALID_HASH_LENGTH]}),
    )


def test_sha1():
    """
    messages:
        - INVALID_HASH
        - INVALID_HASH_LENGTH
    """

    class Data(Model):
        a = SHA1Type()

    INVALID = [
        "_03d40e1a2ede7e31f3c3b45a9e87d12ed33402e",
        "g03d40e1a2ede7e31f3c3b45a9e87d12ed33402e",
        "z03d40e1a2ede7e31f3c3b45a9e87d12ed33402e",
        "G03d40e1a2ede7e31f3c3b45a9e87d12ed33402e",
        # FIXME: PY3: schematics uses integer conversion for validating hex and
        # Py3 integers can contain underscores.
        # 'a03d_0e1a2ede7e31f3c3b45a9e87d12ed33402e',
    ]
    VALID = ["a03d70e1a2ede7e31f3c3b45a9e87d12ed33402e"]
    _test_valid_invalid(
        model=Data, valid=VALID, invalid=INVALID, expected_error=messages.INVALID_HASH
    )
    _test_data(
        model=Data,
        data={"a": "a03d70e1a2ede7e31f3c3b45a9e87d12ed33402"},
        expected=(False, {"a": [messages.INVALID_HASH_LENGTH]}),
    )
    _test_data(
        model=Data,
        data={"a": "8b1a9953c4611296"},
        expected=(False, {"a": [messages.INVALID_HASH_LENGTH]}),
    )
    _test_data(
        model=Data,
        data={"a": "8b1a9953c46112968b1a9953c46112968b1a9953c4611296"},
        expected=(False, {"a": [messages.INVALID_HASH_LENGTH]}),
    )


def test_list():
    """
    messages:
        - INVALID_LIST
        - LIST_TOO_SHORT
        - LIST_TOO_LARGE
        - INVALID_INT
    """

    class Data(Model):
        a = ListType(field=IntType(), min_size=3, max_size=5)

    _test_data(model=Data, data={"a": [1, 2, 3]}, expected=(True, {}))
    _test_data(model=Data, data={"a": ["1", "2", "3"]}, expected=(True, {}))
    _test_data(
        model=Data, data={"a": Data}, expected=(False, {"a": [messages.INVALID_LIST]})
    )
    if SCHEMATICS1:
        _test_data(
            model=Data,
            data={"a": ["a", "b", "c"]},
            expected=(False, {"a": [messages.INVALID_INT]}),
        )
    else:
        _test_data(
            model=Data,
            data={"a": ["a", "b", "c"]},
            expected=(
                False,
                {
                    "a.0": [messages.INVALID_INT],
                    "a.1": [messages.INVALID_INT],
                    "a.2": [messages.INVALID_INT],
                },
            ),
        )
    _test_data(
        model=Data,
        data={"a": [1, 2]},
        expected=(False, {"a": [messages.LIST_TOO_SHORT]}),
    )
    _test_data(
        model=Data,
        data={"a": [1, 2, 3, 4, 5, 6]},
        expected=(False, {"a": [messages.LIST_TOO_LONG]}),
    )


def test_dict():
    """
    messages:
        - INVALID_DICT
        - INVALID_INT
    """

    class Data(Model):
        a = DictType(field=IntType)

    INVALID = ["a", Data]
    VALID = [{}, {"some": 1}]
    if SCHEMATICS1:
        VALID.append([])
    else:
        INVALID.append([])
    _test_valid_invalid(
        model=Data, valid=VALID, invalid=INVALID, expected_error=messages.INVALID_DICT
    )
    if SCHEMATICS1:
        _test_data(
            model=Data,
            data={"a": {"some": "a"}},
            expected=(False, {"a": [messages.INVALID_INT]}),
        )
    else:
        _test_data(
            model=Data,
            data={"a": {"some": "a"}},
            expected=(False, {"a.some": [messages.INVALID_INT]}),
        )


def test_models():
    """
    messages:
        - UNEXPECTED_FIELD
        - MISSING_REQUIRED_FIELD
        - INVALID_FLOAT
    """

    class Coordinates(Model):
        latitude = FloatType(required=True)
        longitude = FloatType(required=True)

    class Geo(Model):
        coordinates = ModelType(Coordinates, required=True)

    class Data(Model):
        geo = ModelType(Geo, required=True)

    _test_data(
        model=Data,
        data={"a": {}},
        expected=(
            False,
            {
                "a": [messages.UNEXPECTED_FIELD],
                "geo": [messages.MISSING_REQUIRED_FIELD],
            },
        ),
    )
    _test_data(
        model=Data,
        data={"geo": None},
        expected=(False, {"geo": [messages.MISSING_REQUIRED_FIELD]}),
    )
    _test_data(
        model=Data,
        data={"geo": {}},
        expected=(False, {"geo.coordinates": [messages.MISSING_REQUIRED_FIELD]}),
    )
    _test_data(
        model=Data,
        data={"geo": {"coordinates": None}},
        expected=(False, {"geo.coordinates": [messages.MISSING_REQUIRED_FIELD]}),
    )
    _test_data(
        model=Data,
        data={"geo": {"coordinates": {}}},
        expected=(
            False,
            {
                "geo.coordinates.latitude": [messages.MISSING_REQUIRED_FIELD],
                "geo.coordinates.longitude": [messages.MISSING_REQUIRED_FIELD],
            },
        ),
    )
    _test_data(
        model=Data,
        data={"geo": {"coordinates": {"latitude": None, "longitude": None}}},
        expected=(
            False,
            {
                "geo.coordinates.latitude": [messages.MISSING_REQUIRED_FIELD],
                "geo.coordinates.longitude": [messages.MISSING_REQUIRED_FIELD],
            },
        ),
    )
    _test_data(
        model=Data,
        data={"geo": {"coordinates": {"latitude": "y", "longitude": "x"}}},
        expected=(
            False,
            {
                "geo.coordinates.latitude": [messages.INVALID_FLOAT],
                "geo.coordinates.longitude": [messages.INVALID_FLOAT],
            },
        ),
    )
    _test_data(
        model=Data,
        data={"geo": {"coordinates": {"latitude": 40.42, "longitude": -3.71}}},
        expected=(True, {}),
    )


def test_multiple_errors_per_field():
    """
    messages:
        - FIELD_TOO_SHORT
        - REGEX_NOT_MATCHED
    """

    class Data(Model):
        a = StringType(min_length=3, regex=r"foo")

    data = {"a": "z"}
    v = SchematicsValidator(Data)
    result = v.validate(data, strict=True)
    assert result[0] is False
    error_messages = result[1]
    assert "a" in error_messages
    expected = [messages.FIELD_TOO_SHORT, messages.REGEX_NOT_MATCHED]
    assert sorted(error_messages["a"]) == expected


def _test_data(model, data, expected, strict=True):
    v = SchematicsValidator(model)
    assert expected == v.validate(data, strict=strict)


def _test_valid_invalid(model, valid, invalid, expected_error, expected_field="a"):
    for dt in valid:
        _test_data(model=model, data={expected_field: dt}, expected=(True, {}))
    for dt in invalid:
        _test_data(
            model=model,
            data={expected_field: dt},
            expected=(False, {expected_field: [expected_error]}),
        )


def test_validation_error_on_model_level_validation():
    class TestModel(Model):
        field_a = StringType()

        def validate_field_a(self, data, value):
            raise ValidationError("Model-level validation failed.")

    _test_data(
        model=TestModel,
        data={"field_a": "some_data"},
        expected=(False, {"field_a": ["Model-level validation failed."]}),
    )
