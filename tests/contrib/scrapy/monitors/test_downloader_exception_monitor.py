import pytest

from spidermon.contrib.scrapy.monitors import (
    DownloaderExceptionMonitor,
)
from spidermon import MonitorSuite
from spidermon.exceptions import NotConfigured
from spidermon import settings


@pytest.fixture
def downloader_exception_suite():
    return MonitorSuite(monitors=[DownloaderExceptionMonitor])


def test_needs_to_configure_downloader_exception_monitor(
    make_data, downloader_exception_suite
):
    data = make_data()
    runner = data.pop("runner")
    data["crawler"].stats.set_value(DownloaderExceptionMonitor.stat_name, 10)
    with pytest.raises(NotConfigured):
        runner.run(downloader_exception_suite, **data)


@pytest.mark.parametrize(
    "value,threshold,expected_status",
    [
        (0, 100, settings.MONITOR.STATUS.SUCCESS),
        (50, 100, settings.MONITOR.STATUS.SUCCESS),
        (99, 100, settings.MONITOR.STATUS.SUCCESS),
        (100, 100, settings.MONITOR.STATUS.SUCCESS),
        (101, 100, settings.MONITOR.STATUS.FAILURE),
        (1000, 1, settings.MONITOR.STATUS.FAILURE),
    ],
)
def test_downloader_exception_monitor_validation(
    make_data, downloader_exception_suite, value, threshold, expected_status
):
    data = make_data({DownloaderExceptionMonitor.threshold_setting: threshold})
    runner = data.pop("runner")

    data["stats"][DownloaderExceptionMonitor.stat_name] = value

    runner.run(downloader_exception_suite, **data)

    assert len(runner.result.monitor_results) == 1
    assert runner.result.monitor_results[0].status == expected_status
