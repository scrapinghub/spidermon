import datetime
import pytest

from spidermon.contrib.scrapy.monitors import (
    PeriodicExecutionTimeMonitor,
    SPIDERMON_MAX_EXECUTION_TIME,
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
