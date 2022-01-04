import pytest

from spidermon.contrib.scrapy.monitors import (
    CriticalCountMonitor,
)
from spidermon import MonitorSuite
from spidermon.exceptions import NotConfigured
from spidermon import settings


@pytest.fixture
def critical_count_suite():
    return MonitorSuite(monitors=[CriticalCountMonitor])


def test_needs_to_configure_critical_count_monitor(make_data, critical_count_suite):
    data = make_data()
    runner = data.pop("runner")
    data["crawler"].stats.set_value("log_count/CRITICAL", 10)
    with pytest.raises(NotConfigured):
        runner.run(critical_count_suite, **data)


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
def test_critical_count_monitor_validation(
    make_data, critical_count_suite, value, threshold, expected_status
):
    data = make_data({CriticalCountMonitor.threshold_setting: threshold})
    runner = data.pop("runner")

    data["stats"]["log_count/CRITICAL"] = value

    runner.run(critical_count_suite, **data)

    assert len(runner.result.monitor_results) == 1
    assert runner.result.monitor_results[0].status == expected_status


def test_critical_count_skip_monitor_if_no_errors(make_data, critical_count_suite):
    data = make_data({CriticalCountMonitor.threshold_setting: 100})
    runner = data.pop("runner")

    data["stats"]["some_stat"] = 1000

    runner.run(critical_count_suite, **data)

    assert len(runner.result.monitor_results) == 1
    assert runner.result.monitor_results[0].status == settings.MONITOR.STATUS.SKIPPED
