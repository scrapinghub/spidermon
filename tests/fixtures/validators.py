from __future__ import absolute_import
import json
from schematics.models import Model
from schematics.types import URLType, StringType, BaseType


class TestValidator(Model):
    url = URLType(required=True)
    title = StringType()


class TreeValidator(Model):
    child = BaseType(required=True)


tree_schema = {
    "$schema": "http://json-schema.org/draft-04/schema",
    "required": ["child"],
    "type": "object",
    "properties": {"child": {"type": "object"}},
}

test_schema = {
    "$schema": "http://json-schema.org/draft-04/schema",
    "required": ["url"],
    "type": "object",
    "properties": {"url": {"type": "string"}, "title": {"type": "string"}},
}

test_schema_string = json.dumps(test_schema)

cerberus_test_schema = {
    "url": {"type": "string", "required": True},
    "title": {"type": "string"},
    }

test_cerberus_schema_string = json.dumps(cerberus_test_schema)

cerberus_tree_schema = {
    "quotes": {
        "type": "dict",
        "schema": {
            "quote": {"type": "string"},
            "author": {"type": "string", "required": True},
        },
    },
    "child": {"empty": False, "type": "string"},
}
