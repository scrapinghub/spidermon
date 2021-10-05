from spidermon import MonitorSuite
from spidermon.contrib.scrapy.monitors import (
    ErrorCountMonitor,
    SPIDERMON_MAX_ERRORS,
)


def new_suite():
    return MonitorSuite(monitors=[ErrorCountMonitor])


def test_log_monitor_should_fail(make_data):
    """Log should fail if the # of error log messages exceed the limit"""
    data = make_data()
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["log_count/ERROR"] = 2
    runner.run(suite, **data)
    assert "Found 2 errors in log" in runner.result.monitor_results[0].error


def test_log_monitor_should_pass(make_data):
    """Log should pass if the # of error log message DOES NOT
    exceed the limit"""
    data = make_data({SPIDERMON_MAX_ERRORS: 50})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["log_count/ERROR"] = 2
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None
