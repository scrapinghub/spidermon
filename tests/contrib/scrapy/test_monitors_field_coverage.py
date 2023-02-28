import pytest
from scrapy import Spider
from scrapy.utils.test import get_crawler

from spidermon import MonitorSuite
from spidermon.contrib.scrapy.monitors import FieldCoverageMonitor
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner
from spidermon.exceptions import NotConfigured


def make_data_for_monitor(settings=None, stats=None):
    crawler = get_crawler(settings_dict=settings or {})
    spider = Spider.from_crawler(crawler, "example.com")
    return {
        "stats": stats or {},
        "crawler": crawler,
        "spider": spider,
        "runner": SpiderMonitorRunner(spider=spider),
        "job": None,
    }


@pytest.fixture
def field_coverage_monitor_suite():
    return MonitorSuite(monitors=[FieldCoverageMonitor])


def test_raise_not_configured_if_add_field_coverage_setting_not_set(
    field_coverage_monitor_suite,
):
    data = make_data_for_monitor()
    monitor_runner = data.pop("runner")
    with pytest.raises(NotConfigured):
        monitor_runner.run(field_coverage_monitor_suite, **data)


def test_raise_not_configured_if_add_field_coverage_setting_set_false(
    field_coverage_monitor_suite,
):
    data = make_data_for_monitor(settings={"SPIDERMON_ADD_FIELD_COVERAGE": False})
    monitor_runner = data.pop("runner")
    with pytest.raises(NotConfigured):
        monitor_runner.run(field_coverage_monitor_suite, **data)


def test_no_error_if_add_field_coverage_setting_set_true(field_coverage_monitor_suite):
    data = make_data_for_monitor(settings={"SPIDERMON_ADD_FIELD_COVERAGE": True})
    monitor_runner = data.pop("runner")
    try:
        monitor_runner.run(field_coverage_monitor_suite, **data)
    except NotConfigured:
        pytest.fail(
            "It should not raise NotConfigured if SPIDERMON_ADD_FIELD_COVERAGE = True"
        )


def test_monitor_fail_if_coverage_less_than_expected(field_coverage_monitor_suite):
    settings = {
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_RULES": {
            "dict/field": 0.8,
        },
    }
    stats = {"spidermon_field_coverage/dict/field": 0.5}
    data = make_data_for_monitor(settings=settings, stats=stats)
    monitor_runner = data.pop("runner")
    monitor_runner.run(field_coverage_monitor_suite, **data)

    assert not monitor_runner.result.wasSuccessful()


def test_monitor_fail_if_no_coverage_from_expected_field(field_coverage_monitor_suite):
    settings = {
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_RULES": {
            "dict/field": 0.8,
        },
    }
    stats = {"spidermon_field_coverage/dict/other_field": 1.0}
    data = make_data_for_monitor(settings=settings, stats=stats)
    monitor_runner = data.pop("runner")
    monitor_runner.run(field_coverage_monitor_suite, **data)

    assert not monitor_runner.result.wasSuccessful()


def test_monitor_pass_if_coverage_equal_than_expected(field_coverage_monitor_suite):
    settings = {
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_RULES": {
            "dict/field": 0.8,
        },
    }
    stats = {"spidermon_field_coverage/dict/field": 0.8}
    data = make_data_for_monitor(settings=settings, stats=stats)
    monitor_runner = data.pop("runner")
    monitor_runner.run(field_coverage_monitor_suite, **data)

    assert monitor_runner.result.wasSuccessful()


def test_monitor_pass_if_coverage_greater_than_expected(field_coverage_monitor_suite):
    settings = {
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_RULES": {
            "dict/field": 0.8,
        },
    }
    stats = {"spidermon_field_coverage/dict/field": 0.9}
    data = make_data_for_monitor(settings=settings, stats=stats)
    monitor_runner = data.pop("runner")
    monitor_runner.run(field_coverage_monitor_suite, **data)

    assert monitor_runner.result.wasSuccessful()


def test_monitor_skip_if_no_items_set_true(field_coverage_monitor_suite):
    settings = {
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_RULES": {
            "dict/field": 0.8,
        },
        "SPIDERMON_FIELD_COVERAGE_SKIP_IF_NO_ITEM": True,
    }
    stats = {"item_scraped_count": 0}
    data = make_data_for_monitor(settings=settings, stats=stats)
    monitor_runner = data.pop("runner")
    monitor_runner.run(field_coverage_monitor_suite, **data)

    assert monitor_runner.result.wasSuccessful()


def test_monitor_skip_if_no_items_set_false(field_coverage_monitor_suite):
    settings = {
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_RULES": {
            "dict/field": 0.8,
        },
    }
    stats = {"item_scraped_count": 0}
    data = make_data_for_monitor(settings=settings, stats=stats)
    monitor_runner = data.pop("runner")
    monitor_runner.run(field_coverage_monitor_suite, **data)

    assert not monitor_runner.result.wasSuccessful()
