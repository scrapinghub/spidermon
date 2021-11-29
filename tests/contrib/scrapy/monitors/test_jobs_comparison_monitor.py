from unittest.mock import Mock

import pytest
from spidermon import MonitorSuite
from spidermon.contrib.scrapy.monitors import (
    SPIDERMON_JOBS_COMPARISON,
    SPIDERMON_JOBS_COMPARISON_STATES,
    SPIDERMON_JOBS_COMPARISON_THRESHOLD,
    JobsComparisonMonitor,
)


@pytest.fixture
def mock_client(previous_counts):
    return Mock(
        **{'spider.jobs.list.return_value': [dict(items=c) for c in previous_counts]}
    )


@pytest.fixture
def mock_suite(mock_client, monkeypatch):
    monkeypatch.setattr(JobsComparisonMonitor, "client", mock_client)
    return MonitorSuite(monitors=[JobsComparisonMonitor])


@pytest.mark.parametrize(
    ["number_of_jobs", "item_count", "previous_counts", "expected"],
    [
        (0, 1, [1], False),
        (1, 0, [1], True),
        (5, 0, [1], True),
    ],
)
def test_jobs_comparison_monitor_is_enabled(
    make_data, mock_suite, item_count, number_of_jobs, expected
):
    data = make_data({SPIDERMON_JOBS_COMPARISON: number_of_jobs})
    data["stats"]["item_scraped_count"] = item_count
    runner = data.pop("runner")
    runner.run(mock_suite, **data)

    is_enabled = runner.result.monitor_results[0].error is not None
    assert is_enabled == expected


@pytest.mark.parametrize(
    ["item_count", "previous_counts", "threshold", "should_raise"],
    [
        (90, [100], 0.9, False),
        (90, [100, 101], 0.9, True),
        (80, [100, 101, 99], 0.8, False),
        (80, [100, 101, 99, 102], 0.8, True),
    ],
)
def test_jobs_comparison_monitor(
    make_data, mock_suite, item_count, threshold, should_raise
):
    data = make_data(
        {SPIDERMON_JOBS_COMPARISON: 1, SPIDERMON_JOBS_COMPARISON_THRESHOLD: threshold}
    )
    data["stats"]["item_scraped_count"] = item_count
    runner = data.pop("runner")
    runner.run(mock_suite, **data)

    assert should_raise == bool(runner.result.monitor_results[0].error)
