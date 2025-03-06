import math
from unittest.mock import Mock, call, patch

import pytest
from spidermon import MonitorSuite
from spidermon.contrib.scrapy.monitors import (
    SPIDERMON_JOBS_COMPARISON,
    SPIDERMON_JOBS_COMPARISON_STATES,
    SPIDERMON_JOBS_COMPARISON_TAGS,
    SPIDERMON_JOBS_COMPARISON_THRESHOLD,
    SPIDERMON_JOBS_COMPARISON_ARGUMENTS,
    SPIDERMON_JOBS_COMPARISON_CLOSE_REASONS,
    ZyteJobsComparisonMonitor,
    monitors,
)
from spidermon.core.factories import MonitorFactory
from spidermon.exceptions import NotConfigured


@pytest.fixture
def mock_jobs(previous_counts):
    return Mock(return_value=[dict(items=c) for c in previous_counts])


@pytest.fixture
def mock_jobs_with_close_reason(previous_job_objs, close_reasons):
    return Mock(
        return_value=[
            dict(items=j["items"], close_reason=j["close_reason"])
            for j in previous_job_objs
            if j["close_reason"] in close_reasons
        ]
    )


@pytest.fixture
def mock_suite(mock_jobs, monkeypatch):
    monkeypatch.setattr(ZyteJobsComparisonMonitor, "_get_jobs", mock_jobs)
    return MonitorSuite(monitors=[ZyteJobsComparisonMonitor])


def get_paginated_jobs(**kwargs):
    mocked_job_meta = []
    for _ in range(kwargs["count"]):
        mocked_job_meta.append({"spider_args": {}})
    return mocked_job_meta


def get_paginated_jobs_with_one_args(**kwargs):
    mocked_job_meta = []
    for _ in range(kwargs["count"]):
        mocked_job_meta.append(
            {"spider_args": {"args1": True}, "close_reason": "finished"}
        )
    return mocked_job_meta


def get_paginated_jobs_arg_finished(**kwargs):
    mocked_job_meta = []
    for _ in range(kwargs["count"]):
        mocked_job_meta.append(
            {"spider_args": {"finished": True}, "close_reason": "finished"}
        )
    return mocked_job_meta


def get_paginated_jobs_with_finished_close_reason(**kwargs):
    objs = []
    for _ in range(kwargs["count"]):
        obj = Mock()
        obj.get.return_value = "finished"
        objs.append(obj)

    return objs


def get_paginated_jobs_with_cancel_close_reason(**kwargs):
    objs = []
    for _ in range(kwargs["count"]):
        obj = Mock()
        obj.get.return_value = "cancel"
        objs.append(obj)

    return objs


@pytest.fixture
def mock_suite_with_close_reason(mock_jobs_with_close_reason, monkeypatch):
    monkeypatch.setattr(
        ZyteJobsComparisonMonitor, "_get_jobs", mock_jobs_with_close_reason
    )
    return MonitorSuite(monitors=[ZyteJobsComparisonMonitor])


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


def test_jobs_comparison_monitor_get_tags_to_filter(monkeypatch):
    mock_data = Mock()

    monitor = TestZyteJobsComparisonMonitor()
    monitor.data = mock_data

    # Empty SPIDERMON_JOBS_COMPARISON_TAGS
    mock_data.crawler.settings.getlist.return_value = None
    assert monitor._get_tags_to_filter() == []

    # Empty SHUB_JOB_DATA.tags
    mock_data.crawler.settings.getlist.return_value = ["tag1", "tag2"]
    assert monitor._get_tags_to_filter() == []

    # Sorted intersection
    mock_data.crawler.settings.getlist.return_value = ["tag2", "tag1", "tag3"]
    monkeypatch.setenv("SHUB_JOB_DATA", '{"tags": ["tag1", "tag2"]}')
    assert monitor._get_tags_to_filter() == ["tag1", "tag2"]


def test_jobs_comparison_monitor_get_jobs():
    mock_client = Mock()
    with patch(
        "spidermon.contrib.scrapy.monitors.monitors.Client"
    ) as mock_client_class:
        mock_client_class.return_value = mock_client
        monitor = TestZyteJobsComparisonMonitor()
        monitor._get_tags_to_filter = Mock(side_effect=lambda: None)
        monitor.data = Mock()
        monitor.crawler.settings.getlist.return_value = None
        monitor.crawler.settings.getbool.return_value = False
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
        monitor.crawler.settings.getlist.return_value = None
        monitor.crawler.settings.getbool.return_value = False
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
        monitor.crawler.settings.getlist.return_value = None
        monitor.crawler.settings.getbool.return_value = False
        mock_client.spider.jobs.list = Mock(side_effect=get_paginated_jobs)

        # Jobs bigger than 1000
        jobs = monitor._get_jobs(states=None, number_of_jobs=2500)
        assert len(jobs) == 2500
        assert mock_client.spider.jobs.list.call_count == 3

    mock_client = Mock()
    with patch(
        "spidermon.contrib.scrapy.monitors.monitors.Client"
    ) as mock_client_class:
        mock_client_class.return_value = mock_client
        monitor = TestZyteJobsComparisonMonitor()
        monitor._get_tags_to_filter = Mock(side_effect=lambda: None)
        monitor.data = Mock()
        monitor.crawler.settings.getlist.return_value = ["finished"]
        monitor.crawler.settings.getbool.return_value = False
        mock_client.spider.jobs.list = Mock(
            side_effect=get_paginated_jobs_with_finished_close_reason
        )

        # Return exact number of jobs
        jobs = monitor._get_jobs(states=None, number_of_jobs=50)
        assert len(jobs) == 50

    mock_client = Mock()
    with patch(
        "spidermon.contrib.scrapy.monitors.monitors.Client"
    ) as mock_client_class:
        mock_client_class.return_value = mock_client
        monitor = TestZyteJobsComparisonMonitor()
        monitor._get_tags_to_filter = Mock(side_effect=lambda: None)
        monitor.data = Mock()
        monitor.crawler.settings.getlist.return_value = ["finished"]
        monitor.crawler.settings.getbool.return_value = False
        mock_client.spider.jobs.list = Mock(
            side_effect=get_paginated_jobs_with_cancel_close_reason
        )

        # Return no jobs as all will be filtered due to close reaseon
        jobs = monitor._get_jobs(states=None, number_of_jobs=50)
        assert len(jobs) == 0

    mock_client = Mock()
    with patch(
        "spidermon.contrib.scrapy.monitors.monitors.Client"
    ) as mock_client_class:
        mock_client_class.return_value = mock_client
        monitor = TestZyteJobsComparisonMonitor()
        monitor._get_tags_to_filter = Mock(side_effect=lambda: None)
        monitor.data = Mock()
        monitor.crawler.settings.getdict.return_value = {}
        monitor.crawler.settings.getlist.return_value = None
        monitor.crawler.settings.getbool.return_value = True
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
        monitor.crawler.settings.getdict.return_value = {"finished": True}
        monitor.crawler.settings.getlist.return_value = ["finished"]
        monitor.crawler.settings.getbool.return_value = True
        mock_client.spider.jobs.list = Mock(side_effect=get_paginated_jobs_arg_finished)

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
        monitor.crawler.settings.getdict.return_value = {"finished": False}
        monitor.crawler.settings.getlist.return_value = ["finished"]
        monitor.crawler.settings.getbool.return_value = True
        mock_client.spider.jobs.list = Mock(side_effect=get_paginated_jobs_arg_finished)

        # Return 0 number of jobs as argument values did not matched
        jobs = monitor._get_jobs(states=None, number_of_jobs=50)
        assert len(jobs) == 0
        mock_client.spider.jobs.list.assert_called_once()

    mock_client = Mock()
    with patch(
        "spidermon.contrib.scrapy.monitors.monitors.Client"
    ) as mock_client_class:
        mock_client_class.return_value = mock_client
        monitor = TestZyteJobsComparisonMonitor()
        monitor._get_tags_to_filter = Mock(side_effect=lambda: None)
        monitor.data = Mock()

        def mock_getlist(key, default=None):
            data = {
                SPIDERMON_JOBS_COMPARISON_CLOSE_REASONS: ["finished"],
            }
            return data.get(key, default)

        monitor.crawler.settings = Mock()
        monitor.crawler.settings.getlist.side_effect = mock_getlist
        monitor.crawler.settings.getdict.return_value = {}
        monitor.crawler.settings.getbool.return_value = True
        mock_client.spider.jobs.list = Mock(side_effect=get_paginated_jobs_arg_finished)

        # Return 0 number of jobs
        jobs = monitor._get_jobs(states=None, number_of_jobs=5)
        assert len(jobs) == 0
        mock_client.spider.jobs.list.assert_called_once()

    mock_client = Mock()
    with patch(
            "spidermon.contrib.scrapy.monitors.monitors.Client"
    ) as mock_client_class:
        mock_client_class.return_value = mock_client
        monitor = TestZyteJobsComparisonMonitor()
        monitor._get_tags_to_filter = Mock(side_effect=lambda: None)
        monitor.data = Mock()

        monitor.crawler.settings = Mock()
        monitor.crawler.settings.getlist.return_value = ["finished"]
        monitor.crawler.settings.getdict.return_value = {"is_debug": False}
        monitor.crawler.settings.getbool.return_value = True
        mock_client.spider.jobs.list = Mock(side_effect=get_paginated_jobs_arg_finished)

        # Return 0 number of jobs
        jobs = monitor._get_jobs(states=None, number_of_jobs=5)
        assert len(jobs) == 0
        mock_client.spider.jobs.list.assert_called_once()


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
            has_tag=list(tags),
        )
        # One call to api every 1000 expected jobs
        for n in range(0, math.ceil(number_of_jobs / 1000))
    ]

    mock_client.spider.jobs.list.assert_has_calls(calls)
