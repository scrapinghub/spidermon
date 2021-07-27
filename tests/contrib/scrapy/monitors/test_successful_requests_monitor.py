from spidermon.contrib.scrapy.monitors import (
    SuccessfulRequestsMonitor,
    SPIDERMON_MIN_SUCCESSFUL_REQUESTS,
)
from spidermon import MonitorSuite


def new_suite():
    return MonitorSuite(monitors=[SuccessfulRequestsMonitor])


def test_successful_requests_monitor_should_fail(make_data):
    """Successful Requests should fail if the successful request count is lower than expected"""

    data = make_data({SPIDERMON_MIN_SUCCESSFUL_REQUESTS: 10})

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/response_status_count/200"] = 3
    runner.run(suite, **data)
    assert "Too few (3) successful requests" in runner.result.monitor_results[0].error


def test_successful_requests_monitor_should_pass_default_nonzero(make_data):
    """Successful Requests should pass if limit is not set"""

    data = make_data({})

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/response_status_count/200"] = 15
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_successful_requests_monitor_should_pass_default_zero(make_data):
    """Successful Requests should pass if limit is not set even if the successful request count is 0"""

    data = make_data({})

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/response_status_count/200"] = 0
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_successful_requests_monitor_should_pass_under_limit(make_data):
    """Successful Requests should pass if the successful request count is not lower than expected"""

    data = make_data({SPIDERMON_MIN_SUCCESSFUL_REQUESTS: 10})

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/response_status_count/200"] = 15
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None
