import datetime
import pytest
from spidermon import settings


from spidermon.contrib.scrapy.monitors import (
    PeriodicExecutionTimeMonitor,
    ItemCountMonitor,
    PeriodicItemCountMonitor,
    SPIDERMON_MAX_EXECUTION_TIME,
    SPIDERMON_ITEM_COUNT_INCREASE,
)
from spidermon import MonitorSuite

# For these tests we treat it as though spider has been running 100 seconds
FAKE_EXECUTION_TIME = 100
FAKE_START_TS = 1632834644


@pytest.fixture
def monitor_suite():
    return MonitorSuite(monitors=[PeriodicExecutionTimeMonitor])


@pytest.fixture
def mock_spider():
    class MockSpider:
        pass

    return MockSpider()


@pytest.fixture
def mock_datetime(mocker):
    mocked_datetime = mocker.patch(
        "spidermon.contrib.scrapy.monitors.monitors.datetime"
    )
    fake_now_dt = datetime.datetime.fromtimestamp(FAKE_START_TS + FAKE_EXECUTION_TIME)

    mocked_datetime.datetime.utcnow.return_value = fake_now_dt
    return mocked_datetime


def test_periodic_execution_monitor_should_fail(
    make_data,
    mock_datetime,
    monitor_suite,
    mock_spider,
):
    """PeriodicExecutionTimeMonitor should fail if start time was too long ago"""
    data = make_data({SPIDERMON_MAX_EXECUTION_TIME: FAKE_EXECUTION_TIME - 1})
    runner = data.pop("runner")
    data["crawler"].spider = mock_spider
    data["crawler"].stats.set_value(
        "start_time", datetime.datetime.fromtimestamp(FAKE_START_TS)
    )
    error_expected = "AssertionError: 100.0 not less than 99 : The job has exceeded the maximum execution time"

    runner.run(monitor_suite, **data)
    for r in runner.result.monitor_results:
        assert error_expected in r.error


def test_periodic_execution_monitor_should_pass(
    make_data,
    mock_datetime,
    monitor_suite,
    mock_spider,
):
    """PeriodicExecutionTimeMonitor should pass if start time was not too long ago"""

    data = make_data({SPIDERMON_MAX_EXECUTION_TIME: FAKE_EXECUTION_TIME + 1})
    runner = data.pop("runner")
    data["crawler"].spider = mock_spider
    data["crawler"].stats.set_value(
        "start_time", datetime.datetime.fromtimestamp(FAKE_START_TS)
    )

    runner.run(monitor_suite, **data)
    for r in runner.result.monitor_results:
        assert r.error is None


def test_periodic_execution_monitor_not_set(make_data, monitor_suite, mock_spider):
    """PeriodicExecutionTimeMonitor should do nothing if threshold not set"""
    data = make_data()
    runner = data.pop("runner")
    runner.run(monitor_suite, **data)
    for r in runner.result.monitor_results:
        assert r.error is None


def test_periodic_execution_monitor_no_start_time(
    make_data, monitor_suite, mock_spider
):
    """PeriodicExecutionTimeMonitor should fail if start time was too long ago"""
    data = make_data({SPIDERMON_MAX_EXECUTION_TIME: 100})
    runner = data.pop("runner")
    runner.run(monitor_suite, **data)
    for r in runner.result.monitor_results:
        assert r.error is None


@pytest.fixture
def item_count_suite():
    return MonitorSuite(monitors=[PeriodicItemCountMonitor])


@pytest.mark.parametrize(
    "item_scraped_count,prev_item_scraped_count,spidermon_item_count_increase,expected_status",
    [
        # Failure since item should increase by 100
        (109, 10, 100, settings.MONITOR.STATUS.FAILURE),
        # Success since item increase by at least 100
        (110, 10, 100, settings.MONITOR.STATUS.SUCCESS),
        # Success because item should increase by more than 25
        # 50 percent of prev_item_scraped_count is 25
        (99, 50, 0.5, settings.MONITOR.STATUS.SUCCESS),
        # Failure because item increase only by 4, expected
        # increase is 5 which is 10 percent of 50
        (54, 50, 0.1, settings.MONITOR.STATUS.FAILURE),
    ],
)
def test_item_count_monitor_validation(
    make_data,
    item_count_suite,
    item_scraped_count,
    prev_item_scraped_count,
    spidermon_item_count_increase,
    expected_status,
):
    data = make_data({SPIDERMON_ITEM_COUNT_INCREASE: spidermon_item_count_increase})
    runner = data.pop("runner")
    data["stats"]["item_scraped_count"] = item_scraped_count
    data["stats"]["prev_item_scraped_count"] = prev_item_scraped_count
    runner.run(item_count_suite, **data)
    assert len(runner.result.monitor_results) == 1
    assert runner.result.monitor_results[0].status == expected_status


def test_item_count_monitor_undefined_stats(make_data, item_count_suite):
    data = make_data({SPIDERMON_ITEM_COUNT_INCREASE: 0})
    data["stats"]["enable_stats"] = 1  # otherwise monitor wont run
    runner = data.pop("runner")
    runner.run(MonitorSuite(monitors=[PeriodicItemCountMonitor]), **data)
    assert runner.result.monitor_results[0].status == settings.MONITOR.STATUS.FAILURE
    runner.run(MonitorSuite(monitors=[PeriodicItemCountMonitor]), **data)
    assert runner.result.monitor_results[0].status == settings.MONITOR.STATUS.FAILURE

    data["stats"]["item_scraped_count"] = 1
    runner.run(MonitorSuite(monitors=[PeriodicItemCountMonitor]), **data)
    assert runner.result.monitor_results[0].status == settings.MONITOR.STATUS.SUCCESS
