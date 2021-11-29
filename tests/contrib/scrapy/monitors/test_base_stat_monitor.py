import pytest
from spidermon.contrib.scrapy.monitors import (
    BaseStatMonitor,
    AssertionType,
)
from spidermon import MonitorSuite
from spidermon.exceptions import NotConfigured
from spidermon import settings


@pytest.mark.parametrize(
    "assertion_type,stat_value,threshold,expected_status",
    [
        (AssertionType.EQ, 90, 100, settings.MONITOR.STATUS.FAILURE),
        (AssertionType.EQ, 100, 100, settings.MONITOR.STATUS.SUCCESS),
        (AssertionType.EQ, 110, 100, settings.MONITOR.STATUS.FAILURE),
        (AssertionType.NEQ, 90, 100, settings.MONITOR.STATUS.SUCCESS),
        (AssertionType.NEQ, 100, 100, settings.MONITOR.STATUS.FAILURE),
        (AssertionType.NEQ, 110, 100, settings.MONITOR.STATUS.SUCCESS),
        (AssertionType.GT, 99, 100, settings.MONITOR.STATUS.FAILURE),
        (AssertionType.GT, 100.1, 100, settings.MONITOR.STATUS.SUCCESS),
        (AssertionType.GT, 100, 100, settings.MONITOR.STATUS.FAILURE),
        (AssertionType.GT, 101, 100, settings.MONITOR.STATUS.SUCCESS),
        (AssertionType.GTE, 99, 100, settings.MONITOR.STATUS.FAILURE),
        (AssertionType.GTE, 100, 100, settings.MONITOR.STATUS.SUCCESS),
        (AssertionType.GTE, 101, 100, settings.MONITOR.STATUS.SUCCESS),
        (AssertionType.LT, 99, 100, settings.MONITOR.STATUS.SUCCESS),
        (AssertionType.LT, 99.9, 100, settings.MONITOR.STATUS.SUCCESS),
        (AssertionType.LT, 100, 100, settings.MONITOR.STATUS.FAILURE),
        (AssertionType.LT, 101, 100, settings.MONITOR.STATUS.FAILURE),
        (AssertionType.LTE, 99, 100, settings.MONITOR.STATUS.SUCCESS),
        (AssertionType.LTE, 100, 100, settings.MONITOR.STATUS.SUCCESS),
        (AssertionType.LTE, 101, 100, settings.MONITOR.STATUS.FAILURE),
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
        assert_type = AssertionType.LT

    data = make_data()
    runner = data.pop("runner")
    data["stats"][TestBaseStatMonitor.stat_name] = 100
    monitor_suite = MonitorSuite(monitors=[TestBaseStatMonitor])

    with pytest.raises(NotConfigured):
        runner.run(monitor_suite, **data)


def test_not_configured_without_threshold_setting_or_method(make_data):
    class TestBaseStatMonitor(BaseStatMonitor):
        stat_name = "test_statistic"
        assert_type = AssertionType.EQ

    data = make_data()
    runner = data.pop("runner")
    data["stats"][TestBaseStatMonitor.stat_name] = 100
    monitor_suite = MonitorSuite(monitors=[TestBaseStatMonitor])

    with pytest.raises(NotConfigured):
        runner.run(monitor_suite, **data)


def test_base_stat_monitor_using_get_threshold_method(make_data):
    class TestBaseStatMonitor(BaseStatMonitor):
        stat_name = "test_statistic"
        assert_type = AssertionType.EQ

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
        assert_type = AssertionType.EQ

    expected_threshold = 100
    obtained_value = 90
    data = make_data({TestBaseStatMonitor.threshold_setting: expected_threshold})

    runner = data.pop("runner")
    data["stats"][TestBaseStatMonitor.stat_name] = obtained_value
    monitor_suite = MonitorSuite(monitors=[TestBaseStatMonitor])

    runner.run(monitor_suite, **data)
    assert (
        runner.result.monitor_results[0].reason
        == f"'{TestBaseStatMonitor.stat_name}' - expected: {TestBaseStatMonitor.assert_type.value}"
        f" to {expected_threshold} - obtained: {obtained_value}",
    )
