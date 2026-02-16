import pytest

pytest.importorskip("scrapy")

from spidermon.contrib.scrapy.monitors import (
    ItemCountMonitor,
)
from spidermon import MonitorSuite
from spidermon.exceptions import NotConfigured
from spidermon import settings


@pytest.fixture
def item_count_suite():
    return MonitorSuite(monitors=[ItemCountMonitor])


def test_needs_to_configure_item_count_monitor(make_data, item_count_suite):
    data = make_data()
    runner = data.pop("runner")
    data["crawler"].stats.set_value("item_scraped_count", 10)
    with pytest.raises(NotConfigured):
        runner.run(item_count_suite, **data)


@pytest.mark.parametrize(
    "value,threshold,expected_status",
    [
        (0, 100, settings.MONITOR.STATUS.FAILURE),
        (50, 100, settings.MONITOR.STATUS.FAILURE),
        (99, 100, settings.MONITOR.STATUS.FAILURE),
        (100, 100, settings.MONITOR.STATUS.SUCCESS),
        (101, 100, settings.MONITOR.STATUS.SUCCESS),
        (1000, 1, settings.MONITOR.STATUS.SUCCESS),
    ],
)
def test_item_count_monitor_validation(
    make_data, item_count_suite, value, threshold, expected_status
):
    data = make_data({ItemCountMonitor.threshold_setting: threshold})
    runner = data.pop("runner")

    data["stats"]["item_scraped_count"] = value

    runner.run(item_count_suite, **data)

    assert len(runner.result.monitor_results) == 1
    assert runner.result.monitor_results[0].status == expected_status
