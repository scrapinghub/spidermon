from unittest.mock import Mock

import pytest
from spidermon import MonitorSuite
from spidermon.contrib.scrapy import monitors
from spidermon.contrib.scrapy.monitors import (
    SPIDERMON_JOBS_COMPARISON,
    SPIDERMON_JOBS_COMPARISON_STATES,
    SPIDERMON_JOBS_COMPARISON_TAGS,
    SPIDERMON_JOBS_COMPARISON_THRESHOLD,
    JobsComparisonMonitor,
)


@pytest.fixture
def mock_jobs(previous_counts):
    return Mock(return_value=[dict(items=c) for c in previous_counts])


@pytest.fixture
def mock_suite(mock_jobs, monkeypatch):
    monkeypatch.setattr(JobsComparisonMonitor, "_get_jobs", mock_jobs)
    return MonitorSuite(monitors=[JobsComparisonMonitor])


@pytest.fixture
def mock_suite_and_zyte_client(monkeypatch):
    monkeypatch.setenv("SHUB_JOB_DATA", '{"tags":["tag1","tag2","tag3"]}')
    monkeypatch.setattr(monitors, "zyte", Mock())
    monitors.zyte.client.spider.jobs.list.return_value = []
    return MonitorSuite(monitors=[monitors.JobsComparisonMonitor]), monitors.zyte


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
    assert (
        is_enabled == expected
        or runner.result.monitor_results[0].reason
        == "Jobs comparison monitor is disabled"
    )


@pytest.mark.parametrize(
    ["item_count", "previous_counts", "threshold", "should_raise"],
    [
        (90, [100], 0.9, False),
        (90, [100, 101], 0.9, True),
        (80, [100, 101, 99], 0.8, False),
        (80, [100, 101, 99, 102], 0.8, True),
    ],
)
def test_jobs_comparison_monitor_threshold(
    make_data, mock_suite, item_count, threshold, should_raise
):
    data = make_data(
        {SPIDERMON_JOBS_COMPARISON: 1, SPIDERMON_JOBS_COMPARISON_THRESHOLD: threshold}
    )
    data["stats"]["item_scraped_count"] = item_count
    runner = data.pop("runner")
    runner.run(mock_suite, **data)

    assert should_raise == bool(runner.result.monitor_results[0].error)


@pytest.mark.parametrize(
    ["states", "number_of_jobs", "tags"],
    [
        (("finished",), 5, ("tag1", "tag2")),
        (("foo", "bar"), 10, ("tag3",)),
    ],
)
def test_arguments_passed_to_zyte_client(
    make_data,
    mock_suite_and_zyte_client,
    states,
    number_of_jobs,
    tags,
):
    data = make_data(
        {
            SPIDERMON_JOBS_COMPARISON: number_of_jobs,
            SPIDERMON_JOBS_COMPARISON_STATES: states,
            SPIDERMON_JOBS_COMPARISON_TAGS: tags,
        }
    )
    suite, zyte_module = mock_suite_and_zyte_client
    runner = data.pop("runner")
    runner.run(suite, **data)

    zyte_module.client.spider.jobs.list.assert_called_with(
        state=list(states),
        count=number_of_jobs,
        filters={"has_tag": list(tags)},
    )
