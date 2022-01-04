import pytest
from scrapy import Spider
from scrapy.utils.test import get_crawler

from spidermon import MonitorSuite
from spidermon.contrib.scrapy.monitors import (
    SPIDERMON_MAX_ITEM_VALIDATION_ERRORS,
    ItemValidationMonitor,
)
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner


def make_data(settings):
    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")
    return {
        "stats": crawler.stats.get_stats(),
        "crawler": crawler,
        "spider": spider,
        "runner": SpiderMonitorRunner(spider=spider),
        "job": None,
    }


@pytest.fixture
def item_validation_monitor_suite():
    return MonitorSuite(monitors=[ItemValidationMonitor])


def test_item_validation_monitor_pass_if_does_not_have_validation_error(
    item_validation_monitor_suite,
):
    data = make_data({})
    runner = data.pop("runner")
    data["stats"]["spidermon/validation/fields/errors"] = 0
    runner.run(item_validation_monitor_suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_item_validation_monitor_pass_if_does_not_have_validation_error_stat(
    item_validation_monitor_suite,
):
    data = make_data({})
    runner = data.pop("runner")
    data["stats"]["dummy"] = ""
    runner.run(item_validation_monitor_suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_item_validation_monitor_fails_if_has_validation_errors(
    item_validation_monitor_suite,
):
    data = make_data({})
    runner = data.pop("runner")
    data["stats"]["spidermon/validation/fields/errors"] = 1
    runner.run(item_validation_monitor_suite, **data)
    assert (
        "Found 1 item validation error. Max allowed is 0."
        in runner.result.monitor_results[0].error
    )


@pytest.mark.parametrize(
    "existing_errors,max_errors_allowed,failed_expected",
    [(0, 5, False), (1, 5, False), (5, 5, False), (6, 5, True)],
)
def test_item_validation_monitor_with_max_error_limit(
    item_validation_monitor_suite, existing_errors, max_errors_allowed, failed_expected
):
    data = make_data({SPIDERMON_MAX_ITEM_VALIDATION_ERRORS: max_errors_allowed})
    runner = data.pop("runner")
    data["stats"]["spidermon/validation/fields/errors"] = existing_errors
    runner.run(item_validation_monitor_suite, **data)

    assert bool(runner.result.failures) is failed_expected
