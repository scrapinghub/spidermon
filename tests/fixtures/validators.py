import json

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

custom_type_schema = {
    "$schema": "http://json-schema.org/draft-04/schema",
    "type": "object",
    "properties": {"title": {"type": "custom"}},
}

custom_types = {"custom": lambda checker, instance: instance == "ok"}
