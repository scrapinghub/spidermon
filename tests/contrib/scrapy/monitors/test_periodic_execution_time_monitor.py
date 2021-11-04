import datetime
import pytest

from spidermon.contrib.scrapy.monitors import (
    PeriodicExecutionTimeMonitor,
    SPIDERMON_MAX_EXECUTION_TIME,
)
from spidermon import MonitorSuite


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
    return mocker.patch("spidermon.contrib.scrapy.monitors.datetime")


def test_periodic_execution_monitor_should_fail(
    make_data, monitor_suite, mock_spider, mock_datetime
):
    """PeriodicExecutionTimeMonitor should fail if start time was too long ago"""
    fake_execution_time = 100
    fake_now_ts = 1632834644
    fake_now_dt = datetime.datetime.fromtimestamp(fake_now_ts)
    fake_start_time_ts = fake_now_ts - fake_execution_time

    mock_datetime.datetime.now.return_value = fake_now_dt
    mock_datetime.datetime.fromtimestamp = datetime.datetime.fromtimestamp

    data = make_data({SPIDERMON_MAX_EXECUTION_TIME: fake_execution_time})
    runner = data.pop("runner")
    data["crawler"].stats.set_value("start_time", fake_start_time_ts * 1000)
    data["crawler"].spider = mock_spider
    error_expected = "AssertionError: 100.0 not less than 100 : The job has exceeded the maximum execution time"

    runner.run(monitor_suite, **data)
    for r in runner.result.monitor_results:
        assert error_expected in r.error


def test_periodic_execution_monitor_should_pass(
    make_data, monitor_suite, mock_spider, mock_datetime
):
    """PeriodicExecutionTimeMonitor should pass if start time was not too long ago"""
    fake_execution_time = 100
    fake_now_ts = 1632834644
    fake_now_dt = datetime.datetime.fromtimestamp(fake_now_ts)
    fake_start_time_ts = fake_now_ts - fake_execution_time

    mock_datetime.datetime.now.return_value = fake_now_dt
    mock_datetime.datetime.fromtimestamp = datetime.datetime.fromtimestamp

    data = make_data({SPIDERMON_MAX_EXECUTION_TIME: fake_execution_time + 1})
    runner = data.pop("runner")
    data["crawler"].stats.set_value("start_time", fake_start_time_ts * 1000)
    data["crawler"].spider = mock_spider

    runner.run(monitor_suite, **data)
    for r in runner.result.monitor_results:
        assert r.error is None


def test_periodic_execution_monitor_not_set(make_data, monitor_suite, mock_spider):
    """PeriodicExecutionTimeMonitor should fail if start time was too long ago"""
    data = make_data()
    runner = data.pop("runner")
    runner.run(monitor_suite, **data)
    for r in runner.result.monitor_results:
        assert r.error is None


def test_periodic_execution_monitor_no_start_time(make_data, monitor_suite, mock_spider):
    """PeriodicExecutionTimeMonitor should fail if start time was too long ago"""
    data = make_data({SPIDERMON_MAX_EXECUTION_TIME: 100})
    runner = data.pop("runner")
    runner.run(monitor_suite, **data)
    for r in runner.result.monitor_results:
        assert r.error is None
