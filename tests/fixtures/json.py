JSON_RESULTS_PASS = """
[
    {
        "result": "PASSED",
        "rule": {
            "level": "HIGH",
            "name": "RULE_OBJECT",
            "type": "rule"
        }
    },
    {
        "result": "PASSED",
        "rule": {
            "level": "HIGH",
            "name": "RULE_EXPRESSION",
            "type": "python_expression"
        }
    },
    {
        "result": "PASSED",
        "rule": {
            "level": "HIGH",
            "name": "RULE_LAMBDA",
            "type": "callable"
        }
    },
    {
        "result": "PASSED",
        "rule": {
            "level": "HIGH",
            "name": "RULE_FUNCTION",
            "type": "callable"
        }
    },
    {
        "result": "PASSED",
        "rule": {
            "level": "HIGH",
            "name": "RULE_TESTCASE.test_method_a",
            "type": "test_case"
        }
    },
    {
        "result": "PASSED",
        "rule": {
            "level": "HIGH",
            "name": "RULE_TESTCASE.test_method_b",
            "type": "test_case"
        }
    }
]
"""

JSON_RESULTS_FAIL = """
[
    {
        "result": "FAILED",
        "rule": {
            "level": "HIGH",
            "name": "RULE_OBJECT",
            "type": "rule"
        }
    },
    {
        "result": "FAILED",
        "rule": {
            "level": "HIGH",
            "name": "RULE_EXPRESSION",
            "type": "python_expression"
        }
    },
    {
        "result": "FAILED",
        "rule": {
            "level": "HIGH",
            "name": "RULE_LAMBDA",
            "type": "callable"
        }
    },
    {
        "result": "FAILED",
        "rule": {
            "level": "HIGH",
            "name": "RULE_FUNCTION",
            "type": "callable"
        }
    },
    {
        "result": "FAILED",
        "rule": {
            "level": "HIGH",
            "name": "RULE_TESTCASE.test_method_a",
            "type": "test_case"
        }
    },
    {
        "result": "FAILED",
        "rule": {
            "level": "HIGH",
            "name": "RULE_TESTCASE.test_method_b",
            "type": "test_case"
        }
    }
]
"""

JSON_RESULTS_ERROR = """
[
    {
        "error": {
            "message": "Stats key 'item_scraped_count' not found."
        },
        "result": "ERROR",
        "rule": {
            "level": "HIGH",
            "name": "RULE_OBJECT",
            "type": "rule"
        }
    },
    {
        "error": {
            "message": "Stats key 'item_scraped_count' not found."
        },
        "result": "ERROR",
        "rule": {
            "level": "HIGH",
            "name": "RULE_EXPRESSION",
            "type": "python_expression"
        }
    },
    {
        "error": {
            "message": "Stats key 'item_scraped_count' not found."
        },
        "result": "ERROR",
        "rule": {
            "level": "HIGH",
            "name": "RULE_LAMBDA",
            "type": "callable"
        }
    },
    {
        "error": {
            "message": "Stats key 'item_scraped_count' not found."
        },
        "result": "ERROR",
        "rule": {
            "level": "HIGH",
            "name": "RULE_FUNCTION",
            "type": "callable"
        }
    },
    {
        "error": {
            "message": "Stats key 'item_scraped_count' not found."
        },
        "result": "ERROR",
        "rule": {
            "level": "HIGH",
            "name": "RULE_TESTCASE.test_method_a",
            "type": "test_case"
        }
    },
    {
        "error": {
            "message": "Stats key 'item_scraped_count' not found."
        },
        "result": "ERROR",
        "rule": {
            "level": "HIGH",
            "name": "RULE_TESTCASE.test_method_b",
            "type": "test_case"
        }
    }
]
"""