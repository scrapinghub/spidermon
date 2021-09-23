from spidermon.contrib.scrapy.monitors import (
    UnwantedHTTPCodesFamilyMonitor,
    SPIDERMON_MAX_CLIENT_HTTP_ERRORS,
    SPIDERMON_MAX_SERVER_HTTP_ERRORS,
)
from spidermon import MonitorSuite


def new_suite():
    return MonitorSuite(monitors=[UnwantedHTTPCodesFamilyMonitor])


def test_unwanted_client_errors_monitor_should_fail_zero(make_data):
    """UnwantedHTTPCodesFamilyMonitor should fail if the # of sum of 4xx response codes exceed the limit.
    The limit is 0.
    """

    data = make_data({SPIDERMON_MAX_CLIENT_HTTP_ERRORS: 0})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/response_status_count/400"] = 2
    data["stats"]["downloader/response_status_count/403"] = 2
    data["stats"]["downloader/response_status_count/404"] = 2
    data["stats"]["downloader/response_status_count/503"] = 21
    runner.run(suite, **data)
    assert "Found 6 client errors in log" in runner.result.monitor_results[0].error


def test_unwanted_client_errors_monitor_should_pass(make_data):
    """UnwantedHTTPCodesFamilyMonitor should pass if the # of sum of 4xx response codes does not exceed the limit.
    The limit is 4.
    UnwantedHTTPCodesFamilyMonitor should pass if the # of sum of 5xx response codes does not exceed the limit.
    The limit is 12.
    """

    data = make_data({SPIDERMON_MAX_CLIENT_HTTP_ERRORS: 5, SPIDERMON_MAX_SERVER_HTTP_ERRORS: 12})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/response_status_count/400"] = 1
    data["stats"]["downloader/response_status_count/404"] = 3
    data["stats"]["downloader/response_status_count/503"] = 4
    data["stats"]["downloader/response_status_count/504"] = 5
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None
