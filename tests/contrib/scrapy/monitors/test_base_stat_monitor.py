import pytest
from spidermon.contrib.scrapy.monitors import (
    BaseStatMonitor,
)
from spidermon import MonitorSuite
from spidermon.exceptions import NotConfigured
from spidermon import settings


@pytest.mark.parametrize(
    "assertion_type,stat_value,threshold,expected_status",
    [
        ("==", 90, 100, settings.MONITOR.STATUS.FAILURE),
        ("==", 100, 100, settings.MONITOR.STATUS.SUCCESS),
        ("==", 110, 100, settings.MONITOR.STATUS.FAILURE),
        ("!=", 90, 100, settings.MONITOR.STATUS.SUCCESS),
        ("!=", 100, 100, settings.MONITOR.STATUS.FAILURE),
        ("!=", 110, 100, settings.MONITOR.STATUS.SUCCESS),
        (">", 99, 100, settings.MONITOR.STATUS.FAILURE),
        (">", 100.1, 100, settings.MONITOR.STATUS.SUCCESS),
        (">", 100, 100, settings.MONITOR.STATUS.FAILURE),
        (">", 101, 100, settings.MONITOR.STATUS.SUCCESS),
        (">=", 99, 100, settings.MONITOR.STATUS.FAILURE),
        (">=", 100, 100, settings.MONITOR.STATUS.SUCCESS),
        (">=", 101, 100, settings.MONITOR.STATUS.SUCCESS),
        ("<", 99, 100, settings.MONITOR.STATUS.SUCCESS),
        ("<", 99.9, 100, settings.MONITOR.STATUS.SUCCESS),
        ("<", 100, 100, settings.MONITOR.STATUS.FAILURE),
        ("<", 101, 100, settings.MONITOR.STATUS.FAILURE),
        ("<=", 99, 100, settings.MONITOR.STATUS.SUCCESS),
        ("<=", 100, 100, settings.MONITOR.STATUS.SUCCESS),
        ("<=", 101, 100, settings.MONITOR.STATUS.FAILURE),
    ],
)
def test_base_stat_monitor_assertion_types(
    make_data, assertion_type, stat_value, threshold, expected_status
):
    class TestBaseStatMonitor(BaseStatMonitor):
        stat_name = "test_statistic"
        threshold_setting = "THRESHOLD_SETTING"
        assert_type = assertion_type

    data = make_data({TestBaseStatMonitor.threshold_setting: threshold})
    runner = data.pop("runner")
    data["stats"][TestBaseStatMonitor.stat_name] = stat_value
    monitor_suite = MonitorSuite(monitors=[TestBaseStatMonitor])

    runner.run(monitor_suite, **data)
    assert runner.result.monitor_results[0].status == expected_status


def test_base_stat_monitor_raise_not_configured_if_setting_not_provided(make_data):
    class TestBaseStatMonitor(BaseStatMonitor):
        stat_name = "test_statistic"
        threshold_setting = "THRESHOLD_SETTING"
        assert_type = "<"

    data = make_data()
    runner = data.pop("runner")
    data["stats"][TestBaseStatMonitor.stat_name] = 100
    monitor_suite = MonitorSuite(monitors=[TestBaseStatMonitor])

    with pytest.raises(NotConfigured):
        runner.run(monitor_suite, **data)


def test_not_configured_without_threshold_setting_or_method(make_data):
    class TestBaseStatMonitor(BaseStatMonitor):
        stat_name = "test_statistic"
        assert_type = "=="

    data = make_data()
    runner = data.pop("runner")
    data["stats"][TestBaseStatMonitor.stat_name] = 100
    monitor_suite = MonitorSuite(monitors=[TestBaseStatMonitor])

    with pytest.raises(NotConfigured):
        runner.run(monitor_suite, **data)


def test_base_stat_monitor_using_get_threshold_method(make_data):
    class TestBaseStatMonitor(BaseStatMonitor):
        stat_name = "test_statistic"
        assert_type = "=="

        def get_threshold(self):
            return 100

    data = make_data()
    runner = data.pop("runner")
    data["stats"][TestBaseStatMonitor.stat_name] = 100
    monitor_suite = MonitorSuite(monitors=[TestBaseStatMonitor])

    runner.run(monitor_suite, **data)
    assert runner.result.monitor_results[0].status == settings.MONITOR.STATUS.SUCCESS


def test_failure_message_describe_values_expected(make_data):
    class TestBaseStatMonitor(BaseStatMonitor):
        stat_name = "test_statistic"
        threshold_setting = "THRESHOLD_SETTING"
        assert_type = "=="

    expected_threshold = 100
    obtained_value = 90
    data = make_data({TestBaseStatMonitor.threshold_setting: expected_threshold})

    runner = data.pop("runner")
    data["stats"][TestBaseStatMonitor.stat_name] = obtained_value
    monitor_suite = MonitorSuite(monitors=[TestBaseStatMonitor])

    runner.run(monitor_suite, **data)
    assert (
        runner.result.monitor_results[0].reason
        == f"Expecting '{TestBaseStatMonitor.stat_name}' to be '{TestBaseStatMonitor.assert_type}' "
        f"to '{expected_threshold}'. Current value: '{obtained_value}'",
    )
