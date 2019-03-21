# -*- coding: utf-8 -*-
from __future__ import absolute_import
from unittest import TestCase

from spidermon.contrib.validation import JSONSchemaValidator
from spidermon.contrib.validation import messages

from slugify import slugify
import six


class SchemaTestCaseMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        def _test_function(data_test):
            def _function(self):
                validator = JSONSchemaValidator(data_test.schema or self.schema)
                assert validator.validate(data_test.data) == (
                    data_test.valid,
                    data_test.expected_errors,
                )

            return _function

        cls = super(SchemaTestCaseMetaclass, mcs).__new__(mcs, name, bases, attrs)
        for dt in getattr(cls, "data_tests", []):
            function_name = "test_%s" % slugify(dt.name, separator="_").lower()
            setattr(cls, function_name, _test_function(dt))
        return cls


class SchemaTest(six.with_metaclass(SchemaTestCaseMetaclass, TestCase)):
    schema = {}
    data_tests = []


class DataTest(object):
    def __init__(self, name, data, valid, expected_errors=None, schema=None):
        self.name = name
        self.data = data
        self.valid = valid
        self.expected_errors = expected_errors or {}
        self.schema = schema


class AdditionalItems(SchemaTest):
    data_tests = [
        DataTest(
            name="additionalItems as schema, additional items match schema",
            schema={"items": [{}], "additionalItems": {"type": "integer"}},
            data=[None, 2, 3, 4],
            valid=True,
        ),
        DataTest(
            name="additionalItems as schema, additional items do not match schema",
            schema={"items": [{}], "additionalItems": {"type": "integer"}},
            data=[None, 2, 3, "foo"],
            valid=False,
            expected_errors={"3": [messages.INVALID_INT]},
        ),
        DataTest(
            name="no additionalItems, all items match schema",
            schema={"items": {}, "additionalItems": False},
            data=[1, 2, 3, 4, 5],
            valid=True,
        ),
        DataTest(
            name="array of items with no additionalItems, no additional items present",
            schema={"items": [{}, {}, {}], "additionalItems": False},
            data=[1, 2, 3],
            valid=True,
        ),
        DataTest(
            name="array of items with no additionalItems, additional items are not permitted",
            schema={"items": [{}, {}, {}], "additionalItems": False},
            data=[1, 2, 3, 4],
            valid=False,
            expected_errors={"": [messages.TOO_MANY_ITEMS]},
        ),
        DataTest(
            name="additionalItems as false without items, valid",
            schema={"additionalItems": False},
            data=[1, 2, 3, 4, 5],
            valid=True,
        ),
        DataTest(
            name="additionalItems as false without items, ignores non-arrays",
            schema={"additionalItems": False},
            data={"foo": "bar"},
            valid=True,
        ),
        DataTest(
            name="additionalItems are allowed by default, only the first item is validated",
            schema={"items": [{"type": "integer"}]},
            data=[1, "foo", False],
            valid=True,
        ),
        DataTest(
            name="array, sequence without extra item",
            schema={
                "type": "array",
                "items": [{"type": "boolean"}, {"type": "integer"}, {"type": "string"}],
                "additionalItems": {"type": "boolean"},
            },
            data=[True, 1, "foo"],
            valid=True,
        ),
        DataTest(
            name="array, sequence with valid extra item",
            schema={
                "type": "array",
                "items": [{"type": "boolean"}, {"type": "integer"}, {"type": "string"}],
                "additionalItems": {"type": "boolean"},
            },
            data=[True, 1, "foo", True],
            valid=True,
        ),
        DataTest(
            name="array, sequence with invalid extra item",
            schema={
                "type": "array",
                "items": [{"type": "boolean"}, {"type": "integer"}, {"type": "string"}],
                "additionalItems": {"type": "boolean"},
            },
            data=[True, 1, "foo", 1],
            valid=False,
            expected_errors={"3": [messages.INVALID_BOOLEAN]},
        ),
    ]


class AdditionalProperties(SchemaTest):
    schema_false = {
        "properties": {"foo": {}, "bar": {}},
        "patternProperties": {"^v": {}},
        "additionalProperties": False,
    }
    schema_allows_schema = {
        "properties": {"foo": {}, "bar": {}},
        "additionalProperties": {"type": "boolean"},
    }
    schema_alone = {"additionalProperties": {"type": "boolean"}}
    schema_no = {"properties": {"foo": {}, "bar": {}}}
    data_tests = [
        DataTest(
            name="schema_false, no additional properties is valid",
            schema=schema_false,
            data={"foo": 1},
            valid=True,
        ),
        DataTest(
            name="schema_false, an additional property is invalid",
            schema=schema_false,
            data={"foo": 1, "bar": 2, "quux": "boom"},
            valid=False,
            expected_errors={
                # Used with jsonschema 2.4.0:
                # '': [messages.UNEXPECTED_FIELD],
                # This changed in jsonschema 2.6.0:
                # https://github.com/Julian/jsonschema/pull/317
                "": [messages.REGEX_NOT_MATCHED]
            },
        ),
        DataTest(
            name="schema_false, ignores non-objects",
            schema=schema_false,
            data=[1, 2, 3],
            valid=True,
        ),
        DataTest(
            name="schema_false, patternProperties are not additional properties",
            schema=schema_false,
            data={"foo": 1, "vroom": 2},
            valid=True,
        ),
        DataTest(
            name="schema_allows_schema, no additional properties",
            schema=schema_allows_schema,
            data={"foo": 1},
            valid=True,
        ),
        DataTest(
            name="schema_allows_schema, additional valid property",
            schema=schema_allows_schema,
            data={"foo": 1, "bar": 2, "quux": True},
            valid=True,
        ),
        DataTest(
            name="schema_allows_schema, additional invalid property",
            schema=schema_allows_schema,
            data={"foo": 1, "bar": 2, "quux": 12},
            valid=False,
            expected_errors={"quux": [messages.INVALID_BOOLEAN]},
        ),
        DataTest(
            name="schema_alone, additional valid property",
            schema=schema_alone,
            data={"foo": True},
            valid=True,
        ),
        DataTest(
            name="schema_alone, additional invalid property",
            schema=schema_alone,
            data={"foo": 1},
            valid=False,
            expected_errors={"foo": [messages.INVALID_BOOLEAN]},
        ),
        DataTest(
            name="schema_no, additional properties are allowed",
            schema=schema_no,
            data={"foo": 1, "bar": 2, "quux": True},
            valid=True,
        ),
    ]


class AllOf(SchemaTest):
    schema = {
        "type": "object",
        "properties": {"A": {"type": "boolean"}, "B": {"type": "boolean"}},
        "allOf": [{"required": ["A"]}, {"required": ["B"]}],
    }
    data_tests = [
        DataTest(
            name="Empty object",
            data={},
            valid=False,
            expected_errors={
                "A": [messages.MISSING_REQUIRED_FIELD],
                "B": [messages.MISSING_REQUIRED_FIELD],
            },
        ),
        DataTest(
            name="Mismatch B",
            data={"A": True},
            valid=False,
            expected_errors={"B": [messages.MISSING_REQUIRED_FIELD]},
        ),
        DataTest(
            name="Mismatch A",
            data={"B": True},
            valid=False,
            expected_errors={"A": [messages.MISSING_REQUIRED_FIELD]},
        ),
        DataTest(name="Both values", data={"A": False, "B": False}, valid=True),
        DataTest(
            name="Wrong type for A",
            data={"A": 1, "B": False},
            valid=False,
            expected_errors={"A": [messages.INVALID_BOOLEAN]},
        ),
        DataTest(
            name="Wrong type for both",
            data={"A": 1, "B": 1},
            valid=False,
            expected_errors={
                "A": [messages.INVALID_BOOLEAN],
                "B": [messages.INVALID_BOOLEAN],
            },
        ),
    ]


class AnyOf(SchemaTest):
    schema = {
        "type": "object",
        "properties": {"A": {"type": "boolean"}, "B": {"type": "boolean"}},
        "anyOf": [{"required": ["A"]}, {"required": ["B"]}],
    }
    data_tests = [
        DataTest(
            name="Empty object",
            data={},
            valid=False,
            expected_errors={"": [messages.NOT_VALID_UNDER_ANY_SCHEMA]},
        ),
        DataTest(name="Mismatch B", data={"A": True}, valid=True),
        DataTest(name="Mismatch A", data={"B": True}, valid=True),
        DataTest(name="Both values", data={"A": False, "B": False}, valid=True),
        DataTest(
            name="Wrong type for A",
            data={"A": 1, "B": False},
            valid=False,
            expected_errors={"A": [messages.INVALID_BOOLEAN]},
        ),
        DataTest(
            name="Wrong type for both",
            data={"A": 1, "B": 1},
            valid=False,
            expected_errors={
                "A": [messages.INVALID_BOOLEAN],
                "B": [messages.INVALID_BOOLEAN],
            },
        ),
    ]


class Dependencies(SchemaTest):
    schema_single = {"dependencies": {"bar": ["foo"]}}
    schema_multiple = {"dependencies": {"quux": ["foo", "bar"]}}
    schema_multiple_subschema = {
        "dependencies": {
            "bar": {
                "properties": {"foo": {"type": "integer"}, "bar": {"type": "integer"}}
            }
        }
    }
    data_tests = [
        DataTest(name="single, neither", schema=schema_single, data={}, valid=True),
        DataTest(
            name="single, nondependant",
            schema=schema_single,
            data={"foo": 1},
            valid=True,
        ),
        DataTest(
            name="single, with dependency",
            schema=schema_single,
            data={"foo": 1, "bar": 2},
            valid=True,
        ),
        DataTest(
            name="single, missing dependency",
            schema=schema_single,
            data={"bar": 2},
            valid=False,
            expected_errors={"": [messages.MISSING_DEPENDENT_FIELD]},
        ),
        DataTest(
            name="single, ignores non-objects",
            schema=schema_single,
            data="foo",
            valid=True,
        ),
        DataTest(name="multiple, neither", schema=schema_multiple, data={}, valid=True),
        DataTest(
            name="multiple, nondependants",
            schema=schema_multiple,
            data={"foo": 1, "bar": 2},
            valid=True,
        ),
        DataTest(
            name="multiple, with dependencies",
            schema=schema_multiple,
            data={"foo": 1, "bar": 2, "quux": 3},
            valid=True,
        ),
        DataTest(
            name="multiple, missing dependency",
            schema=schema_multiple,
            data={"foo": 1, "quux": 2},
            valid=False,
            expected_errors={"": [messages.MISSING_DEPENDENT_FIELD]},
        ),
        DataTest(
            name="multiple, missing other dependency",
            schema=schema_multiple,
            data={"bar": 1, "quux": 2},
            valid=False,
            expected_errors={"": [messages.MISSING_DEPENDENT_FIELD]},
        ),
        DataTest(
            name="multiple, missing both dependencies",
            schema=schema_multiple,
            data={"quux": 1},
            valid=False,
            expected_errors={
                "": [messages.MISSING_DEPENDENT_FIELD, messages.MISSING_DEPENDENT_FIELD]
            },
        ),
        DataTest(
            name="multiple subschema, valid",
            schema=schema_multiple_subschema,
            data={"foo": 1, "bar": 2},
            valid=True,
        ),
        DataTest(
            name="multiple subschema, no dependency",
            schema=schema_multiple_subschema,
            data={"foo": "quux"},
            valid=True,
        ),
        DataTest(
            name="multiple subschema, wrong type",
            schema=schema_multiple_subschema,
            data={"foo": "quux", "bar": 2},
            valid=False,
            expected_errors={"foo": [messages.INVALID_INT]},
        ),
        DataTest(
            name="multiple subschema, wrong type other",
            schema=schema_multiple_subschema,
            data={"foo": 2, "bar": "quux"},
            valid=False,
            expected_errors={"bar": [messages.INVALID_INT]},
        ),
        DataTest(
            name="multiple subschema, wrong type both",
            schema=schema_multiple_subschema,
            data={"foo": "quux", "bar": "quux"},
            valid=False,
            expected_errors={
                "foo": [messages.INVALID_INT],
                "bar": [messages.INVALID_INT],
            },
        ),
    ]


class Enum(SchemaTest):
    schema_simple = {"enum": [1, 2, 3]}
    schema_heterogeneous = {"enum": [6, "foo", [], True, {"foo": 12}]}
    schema_properties = {
        "type": "object",
        "properties": {"foo": {"enum": ["foo"]}, "bar": {"enum": ["bar"]}},
        "required": ["bar"],
    }
    data_tests = [
        DataTest(name="simple, valid", schema=schema_simple, data=1, valid=True),
        DataTest(
            name="simple, invalid",
            schema=schema_simple,
            data=4,
            valid=False,
            expected_errors={"": [messages.VALUE_NOT_IN_CHOICES]},
        ),
        DataTest(
            name="heterogeneous, valid",
            schema=schema_heterogeneous,
            data=[],
            valid=True,
        ),
        DataTest(
            name="heterogeneous, invalid",
            schema=schema_heterogeneous,
            data=None,
            valid=False,
            expected_errors={"": [messages.VALUE_NOT_IN_CHOICES]},
        ),
        DataTest(
            name="heterogeneous, deep valid",
            schema=schema_heterogeneous,
            data={"foo": False},
            valid=False,
            expected_errors={"": [messages.VALUE_NOT_IN_CHOICES]},
        ),
        DataTest(
            name="properties, both valid",
            schema=schema_properties,
            data={"foo": "foo", "bar": "bar"},
            valid=True,
        ),
        DataTest(
            name="properties, missing optional valid",
            schema=schema_properties,
            data={"bar": "bar"},
            valid=True,
        ),
        DataTest(
            name="properties, missing required",
            schema=schema_properties,
            data={"foo": "foo"},
            valid=False,
            expected_errors={"bar": [messages.MISSING_REQUIRED_FIELD]},
        ),
        DataTest(
            name="properties, missing all",
            schema=schema_properties,
            data={},
            valid=False,
            expected_errors={"bar": [messages.MISSING_REQUIRED_FIELD]},
        ),
    ]


class Format(SchemaTest):
    schema = {
        "type": "object",
        "properties": {
            "datetimes": {
                "type": "array",
                "items": {"type": "string", "format": "date-time"},
            },
            "emails": {"type": "array", "items": {"type": "string", "format": "email"}},
            "ipv4s": {"type": "array", "items": {"type": "string", "format": "ipv4"}},
            "ipv6s": {"type": "array", "items": {"type": "string", "format": "ipv6"}},
            "hostnames": {
                "type": "array",
                "items": {"type": "string", "format": "hostname"},
            },
            "urls": {"type": "array", "items": {"type": "string", "format": "url"}},
            "regexes": {
                "type": "array",
                "items": {"type": "string", "format": "regex"},
            },
        },
    }
    data_tests = [
        DataTest(
            name="datetime. valid",
            data={
                "datetimes": ["2013-03-25T12:42:31+00:32", "2013-03-25T22:04:10.04399Z"]
            },
            valid=True,
        ),
        DataTest(
            name="datetime. invalid",
            data={
                "datetimes": [
                    "2015-05-13 13:35:15.718978",
                    "2015-05-13 13:35:15",
                    "13-05-2013",
                ]
            },
            valid=False,
            expected_errors={
                "datetimes.0": [messages.INVALID_DATETIME],
                "datetimes.1": [messages.INVALID_DATETIME],
                "datetimes.2": [messages.INVALID_DATETIME],
            },
        ),
        DataTest(
            name="email. valid",
            data={
                "emails": [
                    "johndoe@domain.com",
                    "john.doe@domain.com",
                    "john.doe@sub.domain.com",
                    "j@sub.domain.com",
                    "j@d.com",
                    "j@domain.co.uk",
                ]
            },
            valid=True,
        ),
        DataTest(
            name="email. invalid",
            data={
                "emails": [
                    "",
                    "johndoe",
                    "johndoe@domain",
                    "johndoe@domain.",
                    "@domain",
                    "@domain.com",
                    "domain.com",
                ]
            },
            valid=False,
            expected_errors={
                "emails.0": [messages.INVALID_EMAIL],
                "emails.1": [messages.INVALID_EMAIL],
                "emails.2": [messages.INVALID_EMAIL],
                "emails.3": [messages.INVALID_EMAIL],
                "emails.4": [messages.INVALID_EMAIL],
                "emails.5": [messages.INVALID_EMAIL],
                "emails.6": [messages.INVALID_EMAIL],
            },
        ),
        DataTest(
            name="ipv4. valid",
            data={
                "ipv4s": [
                    "98.139.180.149",
                    "69.89.31.226",
                    "192.168.1.1",
                    "127.0.0.0",
                    "0.0.0.0",
                    "255.255.255.255",
                ]
            },
            valid=True,
        ),
        DataTest(
            name="ipv4. invalid",
            data={
                "ipv4s": [
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
            },
            valid=False,
            expected_errors={
                "ipv4s.0": [messages.INVALID_IPV4],
                "ipv4s.1": [messages.INVALID_IPV4],
                "ipv4s.2": [messages.INVALID_IPV4],
                "ipv4s.3": [messages.INVALID_IPV4],
                "ipv4s.4": [messages.INVALID_IPV4],
                "ipv4s.5": [messages.INVALID_IPV4],
                "ipv4s.6": [messages.INVALID_IPV4],
                "ipv4s.7": [messages.INVALID_IPV4],
                "ipv4s.8": [messages.INVALID_IPV4],
                "ipv4s.9": [messages.INVALID_IPV4],
                "ipv4s.10": [messages.INVALID_IPV4],
                "ipv4s.11": [messages.INVALID_IPV4],
            },
        ),
        DataTest(
            name="ipv6. valid",
            data={
                "ipv6s": [
                    "2002:4559:1FE2::4559:1FE2",
                    "2002:4559:1FE2:0:0:0:4559:1FE2",
                    "2002:4559:1FE2:0000:0000:0000:4559:1FE2",
                ]
            },
            valid=True,
        ),
        DataTest(
            name="ipv6. invalid",
            data={
                "ipv6s": [
                    "",
                    "98.139.180.149",
                    "69.89.31.226",
                    "192.168.1.1",
                    "127.0.0.0",
                    "0.0.0.0",
                    "255.255.255.255",
                ]
            },
            valid=False,
            expected_errors={
                "ipv6s.0": [messages.INVALID_IPV6],
                "ipv6s.1": [messages.INVALID_IPV6],
                "ipv6s.2": [messages.INVALID_IPV6],
                "ipv6s.3": [messages.INVALID_IPV6],
                "ipv6s.4": [messages.INVALID_IPV6],
                "ipv6s.5": [messages.INVALID_IPV6],
                "ipv6s.6": [messages.INVALID_IPV6],
            },
        ),
        DataTest(
            name="hostname. valid",
            data={
                "hostnames": [
                    "localhost",
                    "google",
                    "google.com",
                    "xn--hxajbheg2az3al.xn--jxalpdlp",
                    "a" * 63,
                ]
            },
            valid=True,
        ),
        DataTest(
            name="hostname. invalid",
            data={"hostnames": ["...", "a" * 64, "-hi-", "_hi_", "*hi*"]},
            valid=False,
            expected_errors={
                "hostnames.0": [messages.INVALID_HOSTNAME],
                "hostnames.1": [messages.INVALID_HOSTNAME],
                "hostnames.2": [messages.INVALID_HOSTNAME],
                "hostnames.3": [messages.INVALID_HOSTNAME],
                "hostnames.4": [messages.INVALID_HOSTNAME],
            },
        ),
        DataTest(
            name="urls. valid",
            data={
                "urls": [
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
            },
            valid=True,
        ),
        DataTest(
            name="urls. invalid",
            data={
                "urls": [
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
            },
            valid=False,
            expected_errors={
                "urls.0": [messages.INVALID_URL],
                "urls.1": [messages.INVALID_URL],
                "urls.2": [messages.INVALID_URL],
                "urls.3": [messages.INVALID_URL],
                "urls.4": [messages.INVALID_URL],
                "urls.5": [messages.INVALID_URL],
                "urls.6": [messages.INVALID_URL],
                "urls.7": [messages.INVALID_URL],
                "urls.8": [messages.INVALID_URL],
                "urls.9": [messages.INVALID_URL],
                "urls.10": [messages.INVALID_URL],
                "urls.11": [messages.INVALID_URL],
                "urls.12": [messages.INVALID_URL],
                "urls.13": [messages.INVALID_URL],
                "urls.14": [messages.INVALID_URL],
                "urls.15": [messages.INVALID_URL],
                "urls.16": [messages.INVALID_URL],
            },
        ),
        DataTest(name="regexes. valid", data={"regexes": ["[0-9]+"]}, valid=True),
        DataTest(
            name="regexes. invalid",
            data={"regexes": ["[0-9]++"]},
            valid=False,
            expected_errors={"regexes.0": [messages.INVALID_REGEX]},
        ),
    ]


class Items(SchemaTest):
    schema_items = {"items": {"type": "integer"}}
    schema_array = {"items": [{"type": "integer"}, {"type": "string"}]}
    data_tests = [
        DataTest(
            name="schema_items. valid items",
            schema=schema_items,
            data=[1, 2, 3],
            valid=True,
        ),
        DataTest(
            name="schema_items. wrong type of items",
            schema=schema_items,
            data=[1, "x"],
            valid=False,
            expected_errors={"1": [messages.INVALID_INT]},
        ),
        DataTest(
            name="schema_items. ignores non-arrays",
            schema=schema_items,
            data={"foo": "bar"},
            valid=True,
        ),
        DataTest(
            name="schema_array. correct types",
            schema=schema_array,
            data=[1, "foo"],
            valid=True,
        ),
        DataTest(
            name="schema_array. wrong types",
            schema=schema_array,
            data=["foo", 1],
            valid=False,
            expected_errors={
                "0": [messages.INVALID_INT],
                "1": [messages.INVALID_STRING],
            },
        ),
    ]


class MaxItems(SchemaTest):
    schema = {"maxItems": 2}
    data_tests = [
        DataTest(name="shorter is valid", data=[1], valid=True),
        DataTest(name="exact length is valid", data=[1, 2], valid=True),
        DataTest(
            name="too long is invalid",
            data=[1, 2, 3],
            valid=False,
            expected_errors={"": [messages.FIELD_TOO_LONG]},
        ),
        DataTest(name="ignores non-arrays", data="foobar", valid=True),
    ]


class MaxLength(SchemaTest):
    schema = {"maxLength": 2}
    data_tests = [
        DataTest(name="shorter is valid", data="f", valid=True),
        DataTest(name="exact length is valid", data="fo", valid=True),
        DataTest(
            name="too long is invalid",
            data="foo",
            valid=False,
            expected_errors={"": [messages.FIELD_TOO_LONG]},
        ),
        DataTest(name="ignores non-strings", data=100, valid=True),
    ]


class MaxProperties(SchemaTest):
    schema = {"maxProperties": 2}
    data_tests = [
        DataTest(name="shorter is valid", data={"foo": 1}, valid=True),
        DataTest(name="exact length is valid", data={"foo": 1, "bar": 2}, valid=True),
        DataTest(
            name="too long is invalid",
            data={"foo": 1, "bar": 2, "baz": 3},
            valid=False,
            expected_errors={"": [messages.TOO_MANY_PROPERTIES]},
        ),
        DataTest(name="ignores non-objects", data="foobar", valid=True),
    ]


class Maximum(SchemaTest):
    # exclusiveMaximum behaviour changed from draft-04 to draft-06
    # http://json-schema.org/draft-06/json-schema-release-notes.html#backwards-incompatible-changes
    schema = {"maximum": 3.0}
    draft4_schema_exclusive = {
        "$schema": "http://json-schema.org/draft-04/schema",
        "maximum": 3.0,
        "exclusiveMaximum": True,
    }
    draft6_schema_exclusive = {
        "$schema": "http://json-schema.org/draft-06/schema",
        "exclusiveMaximum": 3.0,
    }

    data_tests = [
        DataTest(name="below", data=2.6, valid=True),
        DataTest(
            name="above",
            data=3.5,
            valid=False,
            expected_errors={"": [messages.NUMBER_TOO_HIGH]},
        ),
        DataTest(
            name="ignores non-numbers", data={"foo": 1, "bar": 2, "baz": 3}, valid=True
        ),
        DataTest(
            name="draft4 exclusive. below",
            schema=draft4_schema_exclusive,
            data=2.2,
            valid=True,
        ),
        DataTest(
            name="draft4_exclusive. boundary point",
            schema=draft4_schema_exclusive,
            data=3.0,
            valid=False,
            expected_errors={"": [messages.NUMBER_TOO_HIGH]},
        ),
        DataTest(
            name="draft4_exclusive. above",
            schema=draft4_schema_exclusive,
            data=3.5,
            valid=False,
            expected_errors={"": [messages.NUMBER_TOO_HIGH]},
        ),
        DataTest(
            name="draft6 exclusive. below",
            schema=draft6_schema_exclusive,
            data=2.2,
            valid=True,
        ),
        DataTest(
            name="draft6_exclusive. boundary point",
            schema=draft6_schema_exclusive,
            data=3.0,
            valid=False,
            expected_errors={"": [messages.NUMBER_TOO_HIGH]},
        ),
        DataTest(
            name="draft6_exclusive. above",
            schema=draft6_schema_exclusive,
            data=3.5,
            valid=False,
            expected_errors={"": [messages.NUMBER_TOO_HIGH]},
        ),
    ]


class MinItems(SchemaTest):
    schema = {"minItems": 1}
    data_tests = [
        DataTest(name="longer is valid", data=[1, 2], valid=True),
        DataTest(name="exact length is valid", data=[1], valid=True),
        DataTest(
            name="too short is invalid",
            data=[],
            valid=False,
            expected_errors={"": [messages.FIELD_TOO_SHORT]},
        ),
        DataTest(name="ignores non-arrays", data="", valid=True),
    ]


class MinProperties(SchemaTest):
    schema = {"minProperties": 1}
    data_tests = [
        DataTest(name="longer is valid", data={"foo": 1, "bar": 2}, valid=True),
        DataTest(name="exact length is valid", data={"foo": 1}, valid=True),
        DataTest(
            name="too short is invalid",
            data={},
            valid=False,
            expected_errors={"": [messages.NOT_ENOUGH_PROPERTIES]},
        ),
        DataTest(name="ignores non-objects", data="", valid=True),
    ]


class Minimum(SchemaTest):
    # exclusiveMinimum behaviour changed from draft-04 to draft-06
    # http://json-schema.org/draft-06/json-schema-release-notes.html#backwards-incompatible-changes
    schema = {"minimum": 1.1}
    draft4_schema_exclusive = {
        "$schema": "http://json-schema.org/draft-04/schema",
        "minimum": 1.1,
        "exclusiveMinimum": True,
    }
    draft6_schema_exclusive = {
        "$schema": "http://json-schema.org/draft-06/schema",
        "exclusiveMinimum": 1.1,
    }

    data_tests = [
        DataTest(name="above", data=2.6, valid=True),
        DataTest(
            name="below",
            data=0.6,
            valid=False,
            expected_errors={"": [messages.NUMBER_TOO_LOW]},
        ),
        DataTest(name="ignores non-numbers", data="x", valid=True),
        DataTest(
            name="exclusive. above",
            schema=draft4_schema_exclusive,
            data=1.2,
            valid=True,
        ),
        DataTest(
            name="exclusive. above",
            schema=draft6_schema_exclusive,
            data=1.2,
            valid=True,
        ),
        DataTest(
            name="draft4 exclusive. boundary point",
            schema=draft4_schema_exclusive,
            data=1.1,
            valid=False,
            expected_errors={"": [messages.NUMBER_TOO_LOW]},
        ),
        DataTest(
            name="draft6 exclusive. boundary point",
            schema=draft6_schema_exclusive,
            data=1.1,
            valid=False,
            expected_errors={"": [messages.NUMBER_TOO_LOW]},
        ),
        DataTest(
            name="draft4 exclusive. below",
            schema=draft4_schema_exclusive,
            data=0.6,
            valid=False,
            expected_errors={"": [messages.NUMBER_TOO_LOW]},
        ),
        DataTest(
            name="draft6 exclusive. below",
            schema=draft6_schema_exclusive,
            data=0.6,
            valid=False,
            expected_errors={"": [messages.NUMBER_TOO_LOW]},
        ),
    ]


class MultipleOf(SchemaTest):
    schema_int = {"multipleOf": 2}
    schema_number = {"multipleOf": 1.5}
    schema_small_number = {"multipleOf": 0.0001}
    data_tests = [
        DataTest(name="int. valid", schema=schema_int, data=10, valid=True),
        DataTest(name="int. valid float", schema=schema_int, data=10.0, valid=True),
        DataTest(
            name="int. invalid",
            schema=schema_int,
            data=7,
            valid=False,
            expected_errors={"": [messages.NOT_MULTIPLE_OF]},
        ),
        DataTest(name="int. ignores non-numbers", data="x", valid=True),
        DataTest(
            name="number. zero is multiple of anything",
            schema=schema_number,
            data=0,
            valid=True,
        ),
        DataTest(name="number. valid", schema=schema_number, data=4.5, valid=True),
        DataTest(
            name="number. invalid",
            schema=schema_number,
            data=35,
            valid=False,
            expected_errors={"": [messages.NOT_MULTIPLE_OF]},
        ),
        DataTest(
            name="small number. valid",
            schema=schema_small_number,
            data=0.0075,
            valid=True,
        ),
        DataTest(
            name="small number. invalid",
            schema=schema_small_number,
            data=0.00751,
            valid=False,
            expected_errors={"": [messages.NOT_MULTIPLE_OF]},
        ),
    ]


class Not(SchemaTest):
    schema_not = {"not": {"type": "integer"}}
    schema_multiple = {"not": {"type": ["integer", "boolean"]}}
    schema_complex = {
        "not": {"type": "object", "properties": {"foo": {"type": "string"}}}
    }
    schema_forbidden = {"properties": {"foo": {"not": {}}}}
    data_tests = [
        DataTest(name="not. allowed", schema=schema_not, data="foo", valid=True),
        DataTest(
            name="not. disallowed",
            schema=schema_not,
            data=1,
            valid=False,
            expected_errors={"": [messages.NOT_ALLOWED_VALUE]},
        ),
        DataTest(
            name="multiple. allowed", schema=schema_multiple, data="foo", valid=True
        ),
        DataTest(
            name="multiple. mismatch",
            schema=schema_multiple,
            data=1,
            valid=False,
            expected_errors={"": [messages.NOT_ALLOWED_VALUE]},
        ),
        DataTest(
            name="multiple. other mismatch",
            schema=schema_multiple,
            data=True,
            valid=False,
            expected_errors={"": [messages.NOT_ALLOWED_VALUE]},
        ),
        DataTest(name="complex. match", schema=schema_complex, data=1, valid=True),
        DataTest(
            name="complex. other match",
            schema=schema_complex,
            data={"foo": 1},
            valid=True,
        ),
        DataTest(
            name="complex. mismatch",
            schema=schema_complex,
            data={"foo": "bar"},
            valid=False,
            expected_errors={"": [messages.NOT_ALLOWED_VALUE]},
        ),
        DataTest(
            name="forbidden. present",
            schema=schema_forbidden,
            data={"foo": 1, "bar": 2},
            valid=False,
            expected_errors={"foo": [messages.NOT_ALLOWED_VALUE]},
        ),
        DataTest(
            name="forbidden. absent",
            schema=schema_forbidden,
            data={"bar": 1, "baz": 2},
            valid=True,
        ),
    ]


class OneOf(SchemaTest):
    schema = {
        "type": "object",
        "properties": {"A": {"type": "boolean"}, "B": {"type": "boolean"}},
        "oneOf": [{"required": ["A"]}, {"required": ["B"]}],
    }
    data_tests = [
        DataTest(
            name="Empty object",
            data={},
            valid=False,
            expected_errors={"": [messages.NOT_VALID_UNDER_ANY_SCHEMA]},
        ),
        DataTest(name="Mismatch B", data={"A": True}, valid=True),
        DataTest(name="Mismatch A", data={"B": True}, valid=True),
        DataTest(
            name="Both values",
            data={"A": False, "B": False},
            valid=False,
            expected_errors={"": [messages.VALID_FOR_SEVERAL_EXCLUSIVE_SCHEMAS]},
        ),
        DataTest(
            name="Wrong type for A",
            data={"A": 1, "B": False},
            valid=False,
            expected_errors={
                "": [messages.VALID_FOR_SEVERAL_EXCLUSIVE_SCHEMAS],
                "A": [messages.INVALID_BOOLEAN],
            },
        ),
        DataTest(
            name="Wrong type for both",
            data={"A": 1, "B": 1},
            valid=False,
            expected_errors={
                "": [messages.VALID_FOR_SEVERAL_EXCLUSIVE_SCHEMAS],
                "A": [messages.INVALID_BOOLEAN],
                "B": [messages.INVALID_BOOLEAN],
            },
        ),
    ]


class Pattern(SchemaTest):
    schema = {"pattern": "^a*$"}
    data_tests = [
        DataTest(name="valid", data="aaa", valid=True),
        DataTest(
            name="invalid",
            data="abc",
            valid=False,
            expected_errors={"": [messages.REGEX_NOT_MATCHED]},
        ),
        DataTest(name="ignores non-strings", data=True, valid=True),
    ]


class PatternProperties(SchemaTest):
    schema_single = {"patternProperties": {"f.*o": {"type": "integer"}}}
    schema_multiple = {
        "patternProperties": {"a*": {"type": "integer"}, "aaa*": {"maximum": 20}}
    }
    schema_complex = {
        "patternProperties": {
            "[0-9]{2,}": {"type": "boolean"},
            "X_": {"type": "string"},
        }
    }
    data_tests = [
        DataTest(
            name="single. valid", schema=schema_single, data={"foo": 1}, valid=True
        ),
        DataTest(
            name="single. multiple valid",
            schema=schema_single,
            data={"foo": 1, "foooooo": 2},
            valid=True,
        ),
        DataTest(
            name="single. invalid",
            schema=schema_single,
            data={"foo": "bar", "fooooo": 2},
            valid=False,
            expected_errors={"foo": [messages.INVALID_INT]},
        ),
        DataTest(
            name="single. multiple invalid",
            schema=schema_single,
            data={"foo": "bar", "foooooo": "baz"},
            valid=False,
            expected_errors={
                "foo": [messages.INVALID_INT],
                "foooooo": [messages.INVALID_INT],
            },
        ),
        DataTest(
            name="single. ignores non-objects",
            schema=schema_single,
            data=12,
            valid=True,
        ),
        DataTest(
            name="multiple. valid", schema=schema_multiple, data={"a": 21}, valid=True
        ),
        DataTest(
            name="multiple. simultaneous valid",
            schema=schema_multiple,
            data={"aaaa": 18},
            valid=True,
        ),
        DataTest(
            name="multiple. multiple valid",
            schema=schema_multiple,
            data={"a": 21, "aaaa": 18},
            valid=True,
        ),
        DataTest(
            name="multiple. invalid one",
            schema=schema_multiple,
            data={"a": "bar"},
            valid=False,
            expected_errors={"a": [messages.INVALID_INT]},
        ),
        DataTest(
            name="multiple. invalid other",
            schema=schema_multiple,
            data={"aaaa": 31},
            valid=False,
            expected_errors={"aaaa": [messages.NUMBER_TOO_HIGH]},
        ),
        DataTest(
            name="multiple. invalid both",
            schema=schema_multiple,
            data={"aaa": "foo", "aaaa": 31},
            valid=False,
            expected_errors={
                "aaa": [messages.INVALID_INT],
                "aaaa": [messages.NUMBER_TOO_HIGH],
            },
        ),
        DataTest(
            name="complex. non recognized members are ignored",
            schema=schema_complex,
            data={"answer 1": "42"},
            valid=True,
        ),
        DataTest(
            name="complex. recognized members are accounted for",
            schema=schema_complex,
            data={"a31b": None},
            valid=False,
            expected_errors={"a31b": [messages.INVALID_BOOLEAN]},
        ),
        DataTest(
            name="complex. regexes are case sensitive",
            schema=schema_complex,
            data={"a_x_3": 3},
            valid=True,
        ),
        DataTest(
            name="complex. regexes are case sensitive 2",
            schema=schema_complex,
            data={"a_X_3": 3},
            valid=False,
            expected_errors={"a_X_3": [messages.INVALID_STRING]},
        ),
    ]


class Properties(SchemaTest):
    schema = {"properties": {"foo": {"type": "integer"}, "bar": {"type": "string"}}}
    schema_mixed = {
        "properties": {
            "foo": {"type": "array", "maxItems": 3},
            "bar": {"type": "array"},
        },
        "patternProperties": {"f.o": {"minItems": 2}},
        "additionalProperties": {"type": "integer"},
    }
    data_tests = [
        DataTest(name="both present", data={"foo": 1, "bar": "baz"}, valid=True),
        DataTest(
            name="one invalid",
            data={"foo": 1, "bar": {}},
            valid=False,
            expected_errors={"bar": [messages.INVALID_STRING]},
        ),
        DataTest(
            name="both invalid",
            data={"foo": [], "bar": {}},
            valid=False,
            expected_errors={
                "foo": [messages.INVALID_INT],
                "bar": [messages.INVALID_STRING],
            },
        ),
        DataTest(name="other properties", data={"quux": []}, valid=True),
        DataTest(name="ignores non-objects", data=[], valid=True),
        DataTest(
            name="mixed. property validates property",
            schema=schema_mixed,
            data={"foo": [1, 2]},
            valid=True,
        ),
        DataTest(
            name="mixed. property invalidates property",
            schema=schema_mixed,
            data={"foo": [1, 2, 3, 4]},
            valid=False,
            expected_errors={"foo": [messages.FIELD_TOO_LONG]},
        ),
        DataTest(
            name="mixed. patternProperty invalidates property",
            schema=schema_mixed,
            data={"foo": []},
            valid=False,
            expected_errors={"foo": [messages.FIELD_TOO_SHORT]},
        ),
        DataTest(
            name="mixed. patternProperty validates nonproperty",
            schema=schema_mixed,
            data={"fxo": [1, 2]},
            valid=True,
        ),
        DataTest(
            name="mixed. patternProperty invalidates nonproperty",
            schema=schema_mixed,
            data={"fxo": []},
            valid=False,
            expected_errors={"fxo": [messages.FIELD_TOO_SHORT]},
        ),
        DataTest(
            name="mixed. additionalProperty ignores property",
            schema=schema_mixed,
            data={"bar": []},
            valid=True,
        ),
        DataTest(
            name="mixed. additionalProperty validates others",
            schema=schema_mixed,
            data={"quux": 3},
            valid=True,
        ),
        DataTest(
            name="mixed. additionalProperty invalidates others",
            schema=schema_mixed,
            data={"quux": "foo"},
            valid=False,
            expected_errors={"quux": [messages.INVALID_INT]},
        ),
    ]


class Ref(SchemaTest):
    schema_root = {"properties": {"foo": {"$ref": "#"}}, "additionalProperties": False}
    schema_relative = {
        "properties": {"foo": {"type": "integer"}, "bar": {"$ref": "#/properties/foo"}}
    }
    schema_relative_array = {"items": [{"type": "integer"}, {"$ref": "#/items/0"}]}
    schema_escaped = {
        "tilda~field": {"type": "integer"},
        "slash/field": {"type": "integer"},
        "percent%field": {"type": "integer"},
        "properties": {
            "tilda": {"$ref": "#/tilda~0field"},
            "slash": {"$ref": "#/slash~1field"},
            "percent": {"$ref": "#/percent%25field"},
        },
    }
    schema_nested = {
        "definitions": {
            "a": {"type": "integer"},
            "b": {"$ref": "#/definitions/a"},
            "c": {"$ref": "#/definitions/b"},
        },
        "$ref": "#/definitions/c",
    }
    data_tests = [
        DataTest(
            name="root. match", schema=schema_root, data={"foo": False}, valid=True
        ),
        DataTest(
            name="root. recursive match",
            schema=schema_root,
            data={"foo": {"foo": False}},
            valid=True,
        ),
        DataTest(
            name="root. mismatch",
            schema=schema_root,
            data={"bar": False},
            valid=False,
            expected_errors={
                "": [
                    messages.UNEXPECTED_FIELDS.format(
                        unexpected_fields="('bar' was unexpected)"
                    )
                ]
            },
        ),
        DataTest(
            name="root. recursive mismatch",
            schema=schema_root,
            data={"foo": {"bar": False}},
            valid=False,
            expected_errors={
                "foo": [
                    messages.UNEXPECTED_FIELDS.format(
                        unexpected_fields="('bar' was unexpected)"
                    )
                ]
            },
        ),
        DataTest(
            name="relative. match", schema=schema_relative, data={"bar": 3}, valid=True
        ),
        DataTest(
            name="relative. mismatch",
            schema=schema_relative,
            data={"bar": True},
            valid=False,
            expected_errors={"bar": [messages.INVALID_INT]},
        ),
        DataTest(
            name="relative array. match",
            schema=schema_relative_array,
            data=[1, 2],
            valid=True,
        ),
        DataTest(
            name="relative array. mismatch",
            schema=schema_relative_array,
            data=[1, "foo"],
            valid=False,
            expected_errors={"1": [messages.INVALID_INT]},
        ),
        DataTest(
            name="escaped. slash",
            schema=schema_escaped,
            data={"slash": "aoeu"},
            valid=False,
            expected_errors={"slash": [messages.INVALID_INT]},
        ),
        DataTest(
            name="escaped. tilda",
            schema=schema_escaped,
            data={"tilda": "aoeu"},
            valid=False,
            expected_errors={"tilda": [messages.INVALID_INT]},
        ),
        DataTest(
            name="escaped. percent",
            schema=schema_escaped,
            data={"percent": "aoeu"},
            valid=False,
            expected_errors={"percent": [messages.INVALID_INT]},
        ),
        DataTest(
            name="escaped. all",
            schema=schema_escaped,
            data={"slash": "aoeu", "tilda": "aoeu", "percent": "aoeu"},
            valid=False,
            expected_errors={
                "slash": [messages.INVALID_INT],
                "tilda": [messages.INVALID_INT],
                "percent": [messages.INVALID_INT],
            },
        ),
        DataTest(name="nested. valid", schema=schema_nested, data=5, valid=True),
        DataTest(
            name="nested. invalid",
            schema=schema_nested,
            data="a",
            valid=False,
            expected_errors={"": [messages.INVALID_INT]},
        ),
    ]


class Required(SchemaTest):
    schema = {"properties": {"foo": {}, "bar": {}}, "required": ["foo"]}
    schema_default = {"properties": {"foo": {}}}
    data_tests = [
        DataTest(name="valid", data={"foo": 1}, valid=True),
        DataTest(
            name="invalid",
            data={"bar": 1},
            valid=False,
            expected_errors={"foo": [messages.MISSING_REQUIRED_FIELD]},
        ),
        DataTest(
            name="not required by default", schema=schema_default, data={}, valid=True
        ),
    ]


class Type(SchemaTest):
    type_tests = [
        # -------------------------------------------------------
        # type          data        expected error
        # -------------------------------------------------------
        # array
        ("array", [], None),
        ("array", [1, 2], None),
        ("array", None, messages.INVALID_ARRAY),
        ("array", {}, messages.INVALID_ARRAY),
        ("array", "[]", messages.INVALID_ARRAY),
        ("array", "abc", messages.INVALID_ARRAY),
        ("array", 1, messages.INVALID_ARRAY),
        # boolean
        ("boolean", True, None),
        ("boolean", False, None),
        ("boolean", None, messages.INVALID_BOOLEAN),
        ("boolean", "True", messages.INVALID_BOOLEAN),
        ("boolean", "False", messages.INVALID_BOOLEAN),
        ("boolean", 0, messages.INVALID_BOOLEAN),
        ("boolean", 1, messages.INVALID_BOOLEAN),
        # integer
        ("integer", 0, None),
        ("integer", 1, None),
        ("integer", -500, None),
        ("integer", 1000000, None),
        ("integer", None, messages.INVALID_INT),
        ("integer", 1.2, messages.INVALID_INT),
        ("integer", "1", messages.INVALID_INT),
        # number
        ("number", 0, None),
        ("number", 1, None),
        ("number", -500, None),
        ("number", 1000000, None),
        ("number", 1.2, None),
        ("number", -34.7, None),
        ("number", None, messages.INVALID_NUMBER),
        ("number", "1", messages.INVALID_NUMBER),
        ("number", True, messages.INVALID_NUMBER),
        # null
        ("null", None, None),
        ("null", [], messages.NOT_NULL),
        ("null", {}, messages.NOT_NULL),
        ("null", 0, messages.NOT_NULL),
        ("null", "", messages.NOT_NULL),
        # object
        ("object", {}, None),
        ("object", {"a": 1}, None),
        ("object", None, messages.INVALID_OBJECT),
        ("object", [], messages.INVALID_OBJECT),
        ("object", 0, messages.INVALID_OBJECT),
        ("object", "", messages.INVALID_OBJECT),
        ("object", "abc", messages.INVALID_OBJECT),
        # string
        ("string", "", None),
        ("string", "abc", None),
        ("string", "-", None),
        ("string", "...", None),
        ("string", u"", None),
        ("string", u"abc", None),
        ("string", u"España", None),
        ("string", "1", None),
        ("string", None, messages.INVALID_STRING),
        ("string", 1, messages.INVALID_STRING),
        ("string", [], messages.INVALID_STRING),
        ("string", {}, messages.INVALID_STRING),
    ]
    data_tests = [
        DataTest(
            name="%02d_%s" % (i + 1, data_type),
            data=data,
            valid=expected_error is None,
            expected_errors={"": [expected_error]} if expected_error else None,
            schema={"type": data_type},
        )
        for i, (data_type, data, expected_error) in enumerate(type_tests)
    ]


class Unique(SchemaTest):
    schema = {"uniqueItems": True}
    data_tests = [
        DataTest(name="unique array", data=[1, 2], valid=True),
        DataTest(
            name="non-unique array",
            data=[1, 1],
            valid=False,
            expected_errors={"": [messages.NOT_UNIQUE]},
        ),
        DataTest(
            name="non-unique numbers",
            data=[1.0, 1.00, 1],
            valid=False,
            expected_errors={"": [messages.NOT_UNIQUE]},
        ),
        DataTest(
            name="unique objects array",
            data=[{"foo": "bar"}, {"foo": "baz"}],
            valid=True,
        ),
        DataTest(
            name="non-unique objects array",
            data=[{"foo": "bar"}, {"foo": "bar"}],
            valid=False,
            expected_errors={"": [messages.NOT_UNIQUE]},
        ),
        DataTest(
            name="unique nested objects array",
            data=[{"foo": {"bar": {"baz": True}}}, {"foo": {"bar": {"baz": False}}}],
            valid=True,
        ),
        DataTest(
            name="non-unique nested objects array",
            data=[{"foo": {"bar": {"baz": True}}}, {"foo": {"bar": {"baz": True}}}],
            valid=False,
            expected_errors={"": [messages.NOT_UNIQUE]},
        ),
        DataTest(name="unique array of arrays", data=[["foo"], ["bar"]], valid=True),
        DataTest(
            name="non-unique array of arrays",
            data=[["foo"], ["foo"]],
            valid=False,
            expected_errors={"": [messages.NOT_UNIQUE]},
        ),
        DataTest(name="1 and True", data=[1, True], valid=True),
        DataTest(name="0 and False", data=[0, False], valid=True),
        DataTest(
            name="unique heterogeneous types", data=[{}, [1], True, None, 1], valid=True
        ),
        DataTest(
            name="non-unique heterogeneous types",
            data=[{}, [1], True, None, {}, 1],
            valid=False,
            expected_errors={"": [messages.NOT_UNIQUE]},
        ),
    ]
