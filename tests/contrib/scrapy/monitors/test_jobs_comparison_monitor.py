import math
from unittest.mock import Mock, call, patch

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
from spidermon.core.factories import MonitorFactory
from spidermon.exceptions import NotConfigured


@pytest.fixture
def mock_jobs(previous_counts):
    return Mock(return_value=[dict(items=c) for c in previous_counts])


@pytest.fixture
def mock_suite(mock_jobs, monkeypatch):
    monkeypatch.setattr(ZyteJobsComparisonMonitor, "_get_jobs", mock_jobs)
    return MonitorSuite(monitors=[ZyteJobsComparisonMonitor])


def get_paginated_jobs(**kwargs):
    return [Mock() for _ in range(kwargs["count"])]


@pytest.fixture
def mock_suite_and_zyte_client(
    monkeypatch,
    number_of_jobs,
):
    monkeypatch.setenv("SHUB_JOB_DATA", '{"tags":["tag1","tag2","tag3"]}')
    mock_client = Mock()
    mock_client.spider.jobs.list.side_effect = get_paginated_jobs

    monkeypatch.setattr(monitors, "Client", Mock(side_effect=[mock_client]))
    return MonitorSuite(monitors=[monitors.ZyteJobsComparisonMonitor]), mock_client


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


class TestZyteJobsComparisonMonitor(ZyteJobsComparisonMonitor):
    def runTest():
        pass


def test_jobs_comparison_monitor_get_jobs():
    mock_client = Mock()
    with patch(
        "spidermon.contrib.scrapy.monitors.monitors.Client"
    ) as mock_client_class:
        mock_client_class.return_value = mock_client
        monitor = TestZyteJobsComparisonMonitor()
        monitor._get_tags_to_filter = Mock(side_effect=lambda: None)
        monitor.data = Mock()
        mock_client.spider.jobs.list = Mock(side_effect=get_paginated_jobs)

        # Return exact number of jobs
        jobs = monitor._get_jobs(states=None, number_of_jobs=50)
        assert len(jobs) == 50
        mock_client.spider.jobs.list.assert_called_once()

    mock_client = Mock()
    with patch(
        "spidermon.contrib.scrapy.monitors.monitors.Client"
    ) as mock_client_class:
        mock_client_class.return_value = mock_client
        monitor = TestZyteJobsComparisonMonitor()
        monitor._get_tags_to_filter = Mock(side_effect=lambda: None)
        monitor.data = Mock()
        output = [Mock(), Mock()]
        mock_client.spider.jobs.list = Mock(return_value=output)

        # Return less jobs than expected
        jobs = monitor._get_jobs(states=None, number_of_jobs=50)
        assert jobs == output
        mock_client.spider.jobs.list.assert_called_once()

    with patch(
        "spidermon.contrib.scrapy.monitors.monitors.Client"
    ) as mock_client_class:
        mock_client_class.return_value = mock_client
        monitor = TestZyteJobsComparisonMonitor()
        monitor._get_tags_to_filter = Mock(side_effect=lambda: None)
        monitor.data = Mock()
        mock_client.spider.jobs.list = Mock(side_effect=get_paginated_jobs)

        # Jobs bigger than 1000
        jobs = monitor._get_jobs(states=None, number_of_jobs=2500)
        assert len(jobs) == 2500
        assert mock_client.spider.jobs.list.call_count == 3


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
    suite, mock_client = mock_suite_and_zyte_client
    runner = data.pop("runner")
    runner.run(suite, **data)

    calls = [
        call.mock_client.spider.jobs.list(
            start=n * 1000,
            state=list(states),
            # Count goes from pending number of jobs up to 1000
            count=min(number_of_jobs - n * 1000, 1000),
            filters={"has_tag": list(tags)},
        )
        # One call to api every 1000 expected jobs
        for n in range(0, math.ceil(number_of_jobs / 1000))
    ]

    mock_client.spider.jobs.list.assert_has_calls(calls)
