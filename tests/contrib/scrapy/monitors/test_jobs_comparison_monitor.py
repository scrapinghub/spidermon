from unittest.mock import MagicMock

import pytest
from spidermon import MonitorSuite
from spidermon.contrib.scrapy.monitors import (
    SPIDERMON_JOBS_COMPARISON,
    SPIDERMON_JOBS_COMPARISON_STATES,
    SPIDERMON_JOBS_COMPARISON_THRESHOLD,
    JobsComparisonMonitor,
)


@pytest.fixture
def client(previous_counts):
    _client = MagicMock()
    _client.jobs = []
    for count in previous_counts:
        job = MagicMock()
        job.stats.item_scraped_count = count
        _client.jobs.append(job)
    return _client


def new_suite():
    return MonitorSuite(monitors=[JobsComparisonMonitor])


@pytest.mark.parametrize(
    ["previous_jobs", "expected"], [(0, True), (1, True), (5, True)]
)
def test_jobs_comparison_monitor_is_enabled(make_data, previous_jobs, expected):
    data = make_data({SPIDERMON_JOBS_COMPARISON: previous_jobs})
    runner = data.pop("runner")
    runner.run(new_suite(), **data)

    is_enabled = runner.result.monitor_results[0].error is not None
    assert is_enabled == expected
