import pytest

pytest.importorskip("scrapy")

from spidermon.contrib.scrapy.monitors import ItemValidationMonitor
from spidermon import MonitorSuite
from spidermon.exceptions import NotConfigured
from spidermon import settings


@pytest.fixture
def item_validation_suite():
    return MonitorSuite(monitors=[ItemValidationMonitor])


def test_needs_to_configure_item_validation_monitor(make_data, item_validation_suite):
    data = make_data()
    runner = data.pop("runner")
    data["crawler"].stats.set_value(ItemValidationMonitor.stat_name, 10)
    with pytest.raises(NotConfigured):
        runner.run(item_validation_suite, **data)


def test_skip_monitor_if_stat_not_in_job_stats(make_data, item_validation_suite):
    data = make_data({ItemValidationMonitor.threshold_setting: 100})
    runner = data.pop("runner")
    data["crawler"].stats.set_value("item_scraped_count", 10)

    runner.run(item_validation_suite, **data)

    assert len(runner.result.monitor_results) == 1
    assert runner.result.monitor_results[0].status == settings.MONITOR.STATUS.SKIPPED


@pytest.mark.parametrize(
    "value,threshold,expected_status",
    [
        (0, 100, settings.MONITOR.STATUS.SUCCESS),
        (50, 100, settings.MONITOR.STATUS.SUCCESS),
        (99, 100, settings.MONITOR.STATUS.SUCCESS),
        (100, 100, settings.MONITOR.STATUS.SUCCESS),
        (101, 100, settings.MONITOR.STATUS.FAILURE),
        (1000, 1, settings.MONITOR.STATUS.FAILURE),
        (1, 0, settings.MONITOR.STATUS.FAILURE),
    ],
)
def test_item_validation_monitor_validation(
    make_data, item_validation_suite, value, threshold, expected_status
):
    data = make_data({ItemValidationMonitor.threshold_setting: threshold})
    runner = data.pop("runner")

    data["stats"][ItemValidationMonitor.stat_name] = value

    runner.run(item_validation_suite, **data)

    assert len(runner.result.monitor_results) == 1
    assert runner.result.monitor_results[0].status == expected_status
