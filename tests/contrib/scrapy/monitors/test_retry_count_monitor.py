from spidermon.contrib.scrapy.monitors import (
    RetryCountMonitor,
    SPIDERMON_MAX_RETRIES,
)
from spidermon import MonitorSuite


def new_suite():
    return MonitorSuite(monitors=[RetryCountMonitor])


def test_retry_count_monitor_should_fail(make_data):
    """Retry Count should fail if the retry count is higher than expected"""

    data = make_data({SPIDERMON_MAX_RETRIES: 10})

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["retry/max_reached"] = 12
    runner.run(suite, **data)
    assert (
        "Too many requests (12) reached the maximum retry amount"
        in runner.result.monitor_results[0].error
    )


def test_retry_count_monitor_should_pass_disabled(make_data):
    """Retry Count should pass if the limit is negative"""

    data = make_data({SPIDERMON_MAX_RETRIES: -1})

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["retry/max_reached"] = 3
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_retry_count_monitor_should_pass_default(make_data):
    """Retry Count should pass if the limit is not set"""

    data = make_data()

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["retry/max_reached"] = 3
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_retry_count_monitor_should_pass_under_limit(make_data):
    """Retry Count should pass if the retry count is not higher than expected"""

    data = make_data({SPIDERMON_MAX_RETRIES: 10})

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["retry/max_reached"] = 5
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None
