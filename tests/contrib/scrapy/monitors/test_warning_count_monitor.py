from spidermon.contrib.scrapy.monitors import (
    WarningCountMonitor,
    SPIDERMON_MAX_WARNINGS,
)
from spidermon import MonitorSuite


def new_suite():
    return MonitorSuite(monitors=[WarningCountMonitor])


def test_warning_monitor_should_fail(make_data):
    """WarningCount should fail if the # of warning log messages exceed the limit"""

    # Scenario # 1
    data = make_data({SPIDERMON_MAX_WARNINGS: 0})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["log_count/WARNING"] = 2
    runner.run(suite, **data)
    assert "Found 2 warnings in log" in runner.result.monitor_results[0].error

    # Scenario # 2
    data = make_data({SPIDERMON_MAX_WARNINGS: 10})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["log_count/WARNING"] = 12
    runner.run(suite, **data)
    assert "Found 12 warnings in log" in runner.result.monitor_results[0].error


def test_warning_monitor_should_pass(make_data):
    """WarningCount should pass if the # of warning log message DOES NOT
    exceed the limit"""

    # Scenario # 1
    data = make_data({SPIDERMON_MAX_WARNINGS: -1})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["log_count/WARNING"] = 99999
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None

    # Scenario # 2
    data = make_data()
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["log_count/WARNING"] = 99999
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None

    # Scenario # 3
    data = make_data({SPIDERMON_MAX_WARNINGS: 50})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["log_count/WARNING"] = 2
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None
