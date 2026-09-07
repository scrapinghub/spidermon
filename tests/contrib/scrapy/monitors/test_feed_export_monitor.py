import pytest

pytest.importorskip("scrapy")

from spidermon import MonitorSuite, settings
from spidermon.contrib.scrapy.monitors import (
    SPIDERMON_MAX_FEED_EXPORT_FAILURES,
    FeedExportMonitor,
)


def new_suite():
    return MonitorSuite(monitors=[FeedExportMonitor])


def test_feed_export_monitor_passes_without_failures(make_data):
    data = make_data()
    runner = data.pop("runner")

    data["stats"]["feedexport/success_count/FileFeedStorage"] = 1

    runner.run(new_suite(), **data)

    assert runner.result.monitor_results[0].status == settings.MONITOR.STATUS.SUCCESS


def test_feed_export_monitor_passes_without_feedexport_stats(make_data):
    data = make_data()
    runner = data.pop("runner")

    runner.run(new_suite(), **data)

    assert runner.result.monitor_results[0].status == settings.MONITOR.STATUS.SUCCESS


def test_feed_export_monitor_fails_on_failure(make_data):
    data = make_data()
    runner = data.pop("runner")

    data["stats"]["feedexport/failed_count/FileFeedStorage"] = 1

    runner.run(new_suite(), **data)

    assert runner.result.monitor_results[0].status == settings.MONITOR.STATUS.FAILURE
    assert "Found 1 failed feed export(s)" in runner.result.monitor_results[0].error


def test_feed_export_monitor_sums_across_storages(make_data):
    data = make_data()
    runner = data.pop("runner")

    data["stats"]["feedexport/failed_count/FileFeedStorage"] = 1
    data["stats"]["feedexport/failed_count/S3FeedStorage"] = 2

    runner.run(new_suite(), **data)

    assert "Found 3 failed feed export(s)" in runner.result.monitor_results[0].error


def test_feed_export_monitor_respects_threshold_setting(make_data):
    data = make_data({SPIDERMON_MAX_FEED_EXPORT_FAILURES: 2})
    runner = data.pop("runner")

    data["stats"]["feedexport/failed_count/FileFeedStorage"] = 2

    runner.run(new_suite(), **data)

    assert runner.result.monitor_results[0].status == settings.MONITOR.STATUS.SUCCESS
