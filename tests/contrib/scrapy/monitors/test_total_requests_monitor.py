from spidermon.contrib.scrapy.monitors import (
    TotalRequestsMonitor,
    SPIDERMON_MAX_REQUESTS_ALLOWED,
)
from spidermon import MonitorSuite


def new_suite():
    return MonitorSuite(monitors=[TotalRequestsMonitor])


def test_total_requests_monitor_should_fail(make_data):
    """Total Requests should fail if the request count is higher than expected"""

    data = make_data({SPIDERMON_MAX_REQUESTS_ALLOWED: 10})

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/request_count"] = 13
    runner.run(suite, **data)
    assert "Too many (13) requests" in runner.result.monitor_results[0].error


def test_total_requests_monitor_should_pass_disabled(make_data):
    """Total Requests should pass if the limit is negative"""

    data = make_data({SPIDERMON_MAX_REQUESTS_ALLOWED: -1})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/request_count"] = 99999
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_total_requests_monitor_should_pass_default(make_data):
    """Total Requests should pass if the limit is not set"""

    data = make_data({})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/request_count"] = 99999
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_total_requests_monitor_should_pass_under_limit(make_data):
    """Total Requests should pass if the request count is not higher than expected"""

    data = make_data({SPIDERMON_MAX_REQUESTS_ALLOWED: 10})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/request_count"] = 4
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None
