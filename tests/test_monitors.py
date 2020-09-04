import pytest

from scrapy import Spider
from scrapy.crawler import Crawler
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner
from spidermon.contrib.scrapy.monitors import (
    FinishReasonMonitor,
    ItemCountMonitor,
    ErrorCountMonitor,
    UnwantedHTTPCodesMonitor,
    SPIDERMON_MIN_ITEMS,
    SPIDERMON_EXPECTED_FINISH_REASONS,
    SPIDERMON_MAX_ERRORS,
    SPIDERMON_UNWANTED_HTTP_CODES,
    SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT,
)
from spidermon import MonitorSuite
from spidermon.exceptions import NotConfigured


@pytest.fixture
def make_data(request):
    def _make_data(settings=None):
        crawler = Crawler(Spider, settings=settings)
        spider = Spider("dummy")
        return {
            "stats": crawler.stats.get_stats(),
            "crawler": crawler,
            "spider": spider,
            "runner": SpiderMonitorRunner(spider=spider),
            "job": None,
        }

    return _make_data


@pytest.fixture
def item_count_suite():
    return MonitorSuite(monitors=[ItemCountMonitor])


def new_suite(monitors):
    return MonitorSuite(monitors=monitors)


def test_needs_to_configure_item_count_monitor(make_data, item_count_suite):
    """Should raise an exception when ItemCountMonitor it's not configured """
    data = make_data()
    runner = data.pop("runner")
    data["crawler"].stats.set_value("item_scraped_count", 10)
    with pytest.raises(NotConfigured):
        runner.run(item_count_suite, **data)


def test_item_count_monitor_should_fail(make_data, item_count_suite):
    """ItemCount should fail when the desired # of items is not extracted """
    data = make_data({SPIDERMON_MIN_ITEMS: 100})
    runner = data.pop("runner")
    data["stats"]["item_scraped_count"] = 10
    runner.run(item_count_suite, **data)
    for r in runner.result.monitor_results:
        assert "Extracted 10 items, the expected minimum is 100" in r.error


def test_item_count_monitor_extracted_exact_items(make_data, item_count_suite):
    """ItemCount should pass when extract the exact amount of items """
    data = make_data({"SPIDERMON_MIN_ITEMS": 100})
    runner = data.pop("runner")
    data["stats"]["item_scraped_count"] = 100
    runner.run(item_count_suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_item_count_monitor_extracted_more_than_expected(make_data, item_count_suite):
    """ItemCount should pass when extract more than expected amount """
    data = make_data({"SPIDERMON_MIN_ITEMS": 100})
    runner = data.pop("runner")
    data["stats"]["item_scraped_count"] = 500
    runner.run(item_count_suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_item_count_monitor_extracted_less_than_expected(make_data, item_count_suite):
    """ItemCount should fail when extract less than expected amount """
    data = make_data({"SPIDERMON_MIN_ITEMS": 100})
    runner = data.pop("runner")
    data["stats"]["item_scraped_count"] = 50
    runner.run(item_count_suite, **data)
    assert (
        "Extracted 50 items, the expected minimum is 100"
        in runner.result.monitor_results[0].error
    )


def test_finished_reason_monitor_should_fail(make_data):
    """FinishedReason should fail when spider finished with unexpected
    reason"""
    data = make_data()
    runner = data.pop("runner")
    suite = new_suite([FinishReasonMonitor])
    data["stats"]["finish_reason"] = "bad_finish"
    runner.run(suite, **data)
    assert (
        'Finished with "bad_finish" the expected reasons'
        in runner.result.monitor_results[0].error
    )


def test_finished_reason_monitor_should_pass(make_data):
    """FinishedReason should succeed when spider finished with expected
    reason"""
    data = make_data({SPIDERMON_EXPECTED_FINISH_REASONS: "special_reason"})
    runner = data.pop("runner")
    suite = new_suite([FinishReasonMonitor])
    data["stats"]["finish_reason"] = "special_reason"
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_log_monitor_should_fail(make_data):
    """ Log should fail if the # of error log messages exceed the limit """
    data = make_data()
    runner = data.pop("runner")
    suite = new_suite([ErrorCountMonitor])
    data["stats"]["log_count/ERROR"] = 2
    runner.run(suite, **data)
    assert "Found 2 errors in log" in runner.result.monitor_results[0].error


def test_log_monitor_should_pass(make_data):
    """Log should pass if the # of error log message DOES NOT
    exceed the limit"""
    data = make_data({SPIDERMON_MAX_ERRORS: 50})
    runner = data.pop("runner")
    suite = new_suite([ErrorCountMonitor])
    data["stats"]["log_count/ERROR"] = 2
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None


def test_unwanted_httpcodes_should_fail(make_data):
    """Unwanted HTTP Code should fail if # off responses with error status
    codes is higher than expected"""

    # Scenario # 1
    data = make_data({SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT: 16})

    runner = data.pop("runner")
    suite = new_suite([UnwantedHTTPCodesMonitor])
    data["stats"]["downloader/response_status_count/500"] = 17
    data["stats"]["downloader/response_status_count/400"] = 2
    runner.run(suite, **data)
    assert (
        "Found 17 Responses with status code=500"
        in runner.result.monitor_results[0].error
    )

    # Scenario # 2
    data = make_data({SPIDERMON_UNWANTED_HTTP_CODES: [400]})

    runner = data.pop("runner")
    suite = new_suite([UnwantedHTTPCodesMonitor])
    data["stats"]["downloader/response_status_count/400"] = 11
    runner.run(suite, **data)
    assert (
        "Found 11 Responses with status code=400"
        in runner.result.monitor_results[0].error
    )

    # Scenario # 3
    data = make_data(
        {
            SPIDERMON_UNWANTED_HTTP_CODES: [500],
            SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT: 15,
        }
    )

    runner = data.pop("runner")
    suite = new_suite([UnwantedHTTPCodesMonitor])
    data["stats"]["downloader/response_status_count/500"] = 20
    data["stats"]["downloader/response_status_count/400"] = 2
    runner.run(suite, **data)
    assert (
        "Found 20 Responses with status code=500"
        in runner.result.monitor_results[0].error
    )

    # Scenario # 4
    data = make_data({SPIDERMON_UNWANTED_HTTP_CODES: {500: 10, 400: 2}})

    runner = data.pop("runner")
    suite = new_suite([UnwantedHTTPCodesMonitor])
    data["stats"]["downloader/response_status_count/500"] = 8
    data["stats"]["downloader/response_status_count/400"] = 5
    runner.run(suite, **data)
    assert (
        "Found 5 Responses with status code=400"
        in runner.result.monitor_results[0].error
    )

    # Scenario # 5
    data = make_data()
    runner = data.pop("runner")
    suite = new_suite([UnwantedHTTPCodesMonitor])
    data["stats"]["downloader/response_status_count/500"] = 11
    runner.run(suite, **data)
    assert (
        "Found 11 Responses with status code=500"
        in runner.result.monitor_results[0].error
    )


def test_unwanted_httpcodes_should_pass(make_data):
    """Unwanted HTTP Code should pass if # off responses with error status
    codes is lower than expected"""

    # Scenario # 1
    data = make_data({SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT: 16})

    runner = data.pop("runner")
    suite = new_suite([UnwantedHTTPCodesMonitor])
    data["stats"]["downloader/response_status_count/500"] = 16
    data["stats"]["downloader/response_status_count/400"] = 2
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None

    # Scenario # 2
    data = make_data({SPIDERMON_UNWANTED_HTTP_CODES: [400]})

    runner = data.pop("runner")
    suite = new_suite([UnwantedHTTPCodesMonitor])
    data["stats"]["downloader/response_status_count/400"] = 9
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None

    # Scenario # 3
    data = make_data(
        {
            SPIDERMON_UNWANTED_HTTP_CODES: [500],
            SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT: 15,
        }
    )

    runner = data.pop("runner")
    suite = new_suite([UnwantedHTTPCodesMonitor])
    data["stats"]["downloader/response_status_count/500"] = 14
    data["stats"]["downloader/response_status_count/400"] = 2
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None

    # Scenario # 4
    data = make_data({SPIDERMON_UNWANTED_HTTP_CODES: {500: 10, 400: 2}})

    runner = data.pop("runner")
    suite = new_suite([UnwantedHTTPCodesMonitor])
    data["stats"]["downloader/response_status_count/500"] = 8
    data["stats"]["downloader/response_status_count/400"] = 2
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None

    # Scenario # 5
    data = make_data()
    runner = data.pop("runner")
    suite = new_suite([UnwantedHTTPCodesMonitor])
    data["stats"]["downloader/response_status_count/500"] = 9
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None
