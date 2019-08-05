def find_monitor_modules():
    return [
        {
            "path": "spidermon.contrib.scrapy.monitors",
            "monitors": {
                "ItemCountMonitor": {
                    "name": "Item Count",
                    "setting": "SPIDERMON_MIN_ITEMS",
                    "setting_string": "SPIDERMON_MIN_ITEMS = {}",
                    "description": "items",
                    "setting_type": "limit_least",
                },
                "ErrorCountMonitor": {
                    "name": "Error Count",
                    "setting": "SPIDERMON_MAX_ERRORS",
                    "setting_string": "SPIDERMON_MAX_ERRORS = {}",
                    "description": "errors",
                    "setting_type": "limit_most",
                },
                "FinishReasonMonitor": {
                    "name": "Finish Reason",
                    "setting": "SPIDERMON_EXPECTED_FINISH_REASONS",
                    "setting_string": "SPIDERMON_EXPECTED_FINISH_REASONS = {}",
                    "description": "finish reasons",
                    "setting_type": "list",
                },
                "UnwantedHTTPCodesMonitor": {
                    "name": "Unwanted HTTP Codes",
                    "setting": "SPIDERMON_UNWANTED_HTTP_CODES",
                    "setting_string": "SPIDERMON_UNWANTED_HTTP_CODES = {}",
                    "description": "unwanted HTTP codes",
                    "setting_type": "dict",
                },
            },
        }
    ]
