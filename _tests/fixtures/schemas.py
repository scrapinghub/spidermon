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
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "level": {"enum": list(settings.LEVELS)},
                },
                "required": ["name", "type", "level"],
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


ACTION_RESULTS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "state": {"enum": list(settings.ACTION_STATES)},
            "action": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "trigger": {"enum": list(settings.ACTION_TRIGGERS)},
                },
                "required": ["name", "type", "trigger"],
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
        "required": ["state", "action"],
    }
}

ACTION_RESULTS_PROCESSED_SCHEMA = copy.deepcopy(ACTION_RESULTS_SCHEMA)
ACTION_RESULTS_PROCESSED_SCHEMA['items']['properties']['state']['enum'] = [settings.ACTION_STATE_PROCESSED]

ACTION_RESULTS_SKIPPED_SCHEMA = copy.deepcopy(ACTION_RESULTS_SCHEMA)
ACTION_RESULTS_SKIPPED_SCHEMA['items']['properties']['state']['enum'] = [settings.ACTION_STATE_SKIPPED]

ACTION_RESULTS_ERROR_SCHEMA = copy.deepcopy(ACTION_RESULTS_SCHEMA)
ACTION_RESULTS_ERROR_SCHEMA['items']['properties']['state']['enum'] = [settings.ACTION_STATE_ERROR]
ACTION_RESULTS_ERROR_SCHEMA['items']['required'].append('error')
