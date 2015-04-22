import copy

from spidermon import settings


CHECK_RESULTS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "state": {"enum": list(settings.CHECK_STATES)},
            "rule": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "name": {"type": "string"},
                    "level": {"enum": list(settings.LEVELS)},
                },
                "required": ["type", "name", "level"],
            },
            "error": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "traceback": {"type": "string"},
                },
                "required": ["message", "traceback"],
            },
        },
        "required": ["state", "rule"],
    }
}

CHECK_RESULTS_PASS_SCHEMA = copy.deepcopy(CHECK_RESULTS_SCHEMA)
CHECK_RESULTS_PASS_SCHEMA['items']['properties']['state']['enum'] = [settings.CHECK_STATE_PASSED]

CHECK_RESULTS_FAIL_SCHEMA = copy.deepcopy(CHECK_RESULTS_SCHEMA)
CHECK_RESULTS_FAIL_SCHEMA['items']['properties']['state']['enum'] = [settings.CHECK_STATE_FAILED]

CHECK_RESULTS_ERROR_SCHEMA = copy.deepcopy(CHECK_RESULTS_SCHEMA)
CHECK_RESULTS_ERROR_SCHEMA['items']['properties']['state']['enum'] = [settings.CHECK_STATE_ERROR]
CHECK_RESULTS_ERROR_SCHEMA['items']['required'].append('error')
