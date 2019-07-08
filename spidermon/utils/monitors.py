def find_monitor_modules():
    return [
        {
            "path": "spidermon.contrib.scrapy.monitors",
            "monitors": {
                "ItemCountMonitor": {
                    "name": "Item Count Monitor",
                    "setting": "SPIDERMON_MIN_ITEMS",
                    "setting_string": "SPIDERMON_MIN_ITEMS = {}",
                    "description": "items",
                    "categories": ["limit_least"],
                },
                "ErrorCountMonitor": {
                    "name": "Error Count Monitor",
                    "setting": "SPIDERMON_MAX_ERRORS",
                    "setting_string": "SPIDERMON_MAX_ERRORS = {}",
                    "description": "errors",
                    "categories": ["limit_most"],
                },
                "FinishReasonMonitor": {
                    "name": "Finish Reason Monitor",
                    "setting": "SPIDERMON_EXPECTED_FINISH_REASONS",
                    "setting_string": "SPIDERMON_EXPECTED_FINISH_REASONS = {}",
                    "description": "finish reasons",
                    "categories": ["list"],
                },
                "UnwantedHTTPCodesMonitor": {
                    "name": "Unwanted HTTP Code Monitor",
                    "setting": "SPIDERMON_UNWANTED_HTTP_CODES",
                    "setting_string": "SPIDERMON_UNWANTED_HTTP_CODES = {}",
                    "description": "unwanted HTTP codes",
                    "categories": ["limit_most", "list"],
                },
            },
        }
    ]
