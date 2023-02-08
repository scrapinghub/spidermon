from unittest.mock import Mock, call

import pytest
from spidermon import MonitorSuite
from spidermon.contrib.scrapy.monitors import (
    SPIDERMON_JOBS_COMPARISON,
    SPIDERMON_JOBS_COMPARISON_STATES,
    SPIDERMON_JOBS_COMPARISON_TAGS,
    SPIDERMON_JOBS_COMPARISON_THRESHOLD,
    ZyteJobsComparisonMonitor,
    monitors,
)
from spidermon.exceptions import NotConfigured


@pytest.fixture
def mock_jobs(previous_counts):
    return Mock(return_value=[dict(items=c) for c in previous_counts])


@pytest.fixture
def mock_suite(mock_jobs, monkeypatch):
    monkeypatch.setattr(ZyteJobsComparisonMonitor, "_get_jobs", mock_jobs)
    return MonitorSuite(monitors=[ZyteJobsComparisonMonitor])


@pytest.fixture
def mock_suite_and_zyte_client(
    monkeypatch,
    number_of_jobs,
):
    def get_paginated_jobs(**kwargs):
        start = kwargs["start"]
        if start < number_of_jobs:
            return [
                Mock() for _ in range(start, max(number_of_jobs - 1000, number_of_jobs))
            ]
        return []

    monkeypatch.setenv("SHUB_JOB_DATA", '{"tags":["tag1","tag2","tag3"]}')

    monkeypatch.setattr(monitors, "zyte", Mock())
    monitors.zyte.client.spider.jobs.list.side_effect = get_paginated_jobs

    return MonitorSuite(monitors=[monitors.ZyteJobsComparisonMonitor]), monitors.zyte


@pytest.mark.parametrize(
    [
        "number_of_jobs",
        "threshold",
        "item_count",
        "previous_counts",
        "expected_to_be_enabled",
    ],
    [
        (0, 0, 1, [1], False),
        (0, 0.5, 1, [1], False),
        (1, 0, 1, [1], False),
        (-1, 0.5, 1, [1], False),
        (1, -0.5, 1, [1], False),
        (-1, -0.5, 1, [1], False),
        (1, 0.5, 1, [1], True),
        (5, 0.5, 1, [1], True),
        (5, 1.1, 1, [1], True),
    ],
)
def test_jobs_comparison_monitor_is_enabled(
    make_data, mock_suite, item_count, number_of_jobs, expected_to_be_enabled, threshold
):
    data = make_data(
        {
            SPIDERMON_JOBS_COMPARISON: number_of_jobs,
            SPIDERMON_JOBS_COMPARISON_THRESHOLD: threshold,
        }
    )
    data["stats"]["item_scraped_count"] = item_count
    runner = data.pop("runner")

    if expected_to_be_enabled:
        try:
            runner.run(mock_suite, **data)
        except NotConfigured:
            pytest.fail("RAISED NotConfigured exception")
    else:
        with pytest.raises(NotConfigured):
            runner.run(mock_suite, **data)


@pytest.mark.parametrize(
    ["item_count", "previous_counts", "threshold", "should_raise"],
    [
        (90, [100], 0.9, False),
        (80, [100, 101, 99], 0.8, False),
        (90, [100, 100], 0.9, False),
        (111, [100, 100], 1.1, False),
        (100, [100, 100], 1.1, True),
        (90, [100, 101], 0.9, True),
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
    ["states", "number_of_jobs", "tags", "threshold"],
    [
        (("finished",), 5, ("tag1", "tag2"), 0.5),
        (("foo", "bar"), 10, ("tag3",), 0.5),
        (("foo", "bar"), 1001, ("tag3",), 0.5),
        (("foo", "bar"), 2000, ("tag3",), 0.5),
    ],
)
def test_arguments_passed_to_zyte_client(
    make_data,
    mock_suite_and_zyte_client,
    states,
    number_of_jobs,
    tags,
    threshold,
):
    data = make_data(
        {
            SPIDERMON_JOBS_COMPARISON: number_of_jobs,
            SPIDERMON_JOBS_COMPARISON_STATES: states,
            SPIDERMON_JOBS_COMPARISON_TAGS: tags,
            SPIDERMON_JOBS_COMPARISON_THRESHOLD: threshold,
        }
    )
    suite, zyte_module = mock_suite_and_zyte_client
    runner = data.pop("runner")
    runner.run(suite, **data)

    calls = [
        call.zyte_module.client.spider.jobs.list(
            start=n,
            state=list(states),
            count=number_of_jobs,
            filters={"has_tag": list(tags)},
        )
        for n in range(0, number_of_jobs + 1000, 1000)
    ]

    zyte_module.client.spider.jobs.list.assert_has_calls(calls)
