MONITOR_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "description": {"type": "string", "minLength": 1},
        "tests": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "description": {"type": "string", "minLength": 1},
                    "expression": {"type": "string", "minLength": 1},
                    "fail_reason": {"type": "string", "minLength": 1},
                },
                "required": ["name", "expression"],
            },
        },
    },
    "required": ["name", "tests"],
}
