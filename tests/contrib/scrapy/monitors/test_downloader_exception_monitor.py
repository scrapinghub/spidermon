from spidermon.contrib.scrapy.monitors import (
    DownloaderExceptionMonitor,
    SPIDERMON_MAX_DOWNLOADER_EXCEPTIONS,
)
from spidermon import MonitorSuite


def new_suite():
    return MonitorSuite(monitors=[DownloaderExceptionMonitor])


def test_downloader_exception_monitor_should_fail(make_data):
    """Downloader Exceptions should fail if the downloader exceptions count is higher than expected"""

    data = make_data({SPIDERMON_MAX_DOWNLOADER_EXCEPTIONS: 10})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/exception_count"] = 12
    runner.run(suite, **data)
    assert (
        "Too many downloader exceptions (12)" in runner.result.monitor_results[0].error
    )


def test_downloader_exception_monitor_should_pass_disabled(make_data):
    """Downloader Exceptions should pass if the limit is negative"""

    data = make_data({SPIDERMON_MAX_DOWNLOADER_EXCEPTIONS: -1})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/exception_count"] = 99999
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_downloader_exception_monitor_should_pass_default(make_data):
    """Downloader Exceptions should pass if the limit is not set"""

    data = make_data()
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/exception_count"] = 99999
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_downloader_exception_monitor_should_pass_under_limit(make_data):
    """Downloader Exceptions should pass if the downloader exceptions count is not higher than expected"""

    data = make_data({SPIDERMON_MAX_DOWNLOADER_EXCEPTIONS: 10})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/exception_count"] = 3
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None
