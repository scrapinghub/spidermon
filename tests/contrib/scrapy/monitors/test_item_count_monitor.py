import pytest

from spidermon.contrib.scrapy.monitors import (
    ItemCountMonitor,
    SPIDERMON_MIN_ITEMS,
)
from spidermon import MonitorSuite
from spidermon.exceptions import NotConfigured


@pytest.fixture
def item_count_suite():
    return MonitorSuite(monitors=[ItemCountMonitor])


def test_needs_to_configure_item_count_monitor(make_data, item_count_suite):
    """Should raise an exception when ItemCountMonitor it's not configured """
    data = make_data()
    runner = data.pop("runner")
    data["crawler"].stats.set_value("item_scraped_count", 10)
    with pytest.raises(NotConfigured):
        runner.run(item_count_suite, **data)


def test_item_count_monitor_should_fail(make_data, item_count_suite):
    """ItemCount should fail when the desired # of items is not extracted """
    data = make_data({SPIDERMON_MIN_ITEMS: 100})
    runner = data.pop("runner")
    data["stats"]["item_scraped_count"] = 10
    runner.run(item_count_suite, **data)
    for r in runner.result.monitor_results:
        assert "Extracted 10 items, the expected minimum is 100" in r.error


def test_item_count_monitor_extracted_exact_items(make_data, item_count_suite):
    """ItemCount should pass when extract the exact amount of items """
    data = make_data({"SPIDERMON_MIN_ITEMS": 100})
    runner = data.pop("runner")
    data["stats"]["item_scraped_count"] = 100
    runner.run(item_count_suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_item_count_monitor_extracted_more_than_expected(make_data, item_count_suite):
    """ItemCount should pass when extract more than expected amount """
    data = make_data({"SPIDERMON_MIN_ITEMS": 100})
    runner = data.pop("runner")
    data["stats"]["item_scraped_count"] = 500
    runner.run(item_count_suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_item_count_monitor_extracted_less_than_expected(make_data, item_count_suite):
    """ItemCount should fail when extract less than expected amount """
    data = make_data({"SPIDERMON_MIN_ITEMS": 100})
    runner = data.pop("runner")
    data["stats"]["item_scraped_count"] = 50
    runner.run(item_count_suite, **data)
    assert (
        "Extracted 50 items, the expected minimum is 100"
        in runner.result.monitor_results[0].error
    )
