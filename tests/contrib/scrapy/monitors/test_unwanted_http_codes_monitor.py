import pytest

pytest.importorskip("scrapy")

from spidermon import MonitorSuite
from spidermon.contrib.scrapy.monitors import (
    SPIDERMON_UNWANTED_HTTP_CODES,
    SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT,
    UnwantedHTTPCodesMonitor,
)


def new_suite():
    return MonitorSuite(monitors=[UnwantedHTTPCodesMonitor])


def test_unwanted_httpcodes_should_fail(make_data):
    """Unwanted HTTP Code should fail if # off responses with error status
    codes is higher than expected
    """
    # Scenario # 1
    data = make_data({SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT: 16})

    runner = data.pop("runner")
    suite = new_suite()
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
    suite = new_suite()
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
        },
    )

    runner = data.pop("runner")
    suite = new_suite()
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
    suite = new_suite()
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
    suite = new_suite()
    data["stats"]["downloader/response_status_count/500"] = 11
    runner.run(suite, **data)
    assert (
        "Found 11 Responses with status code=500"
        in runner.result.monitor_results[0].error
    )

    # Scenario # 6
    data = make_data({SPIDERMON_UNWANTED_HTTP_CODES: {500: {"max_count": 5}, 400: 2}})

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/request_count"] = 10
    data["stats"]["downloader/response_status_count/500"] = 8
    data["stats"]["downloader/response_status_count/400"] = 1
    runner.run(suite, **data)
    assert (
        "Found 8 Responses with status code=500"
        in runner.result.monitor_results[0].error
    )
    assert "limit of 5" in runner.result.monitor_results[0].error

    # Scenario # 7
    data = make_data(
        {SPIDERMON_UNWANTED_HTTP_CODES: {500: {"max_percentage": 0.5}, 400: 2}},
    )

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/request_count"] = 10
    data["stats"]["downloader/response_status_count/500"] = 8
    data["stats"]["downloader/response_status_count/400"] = 1
    runner.run(suite, **data)
    assert (
        "Found 8 Responses with status code=500"
        in runner.result.monitor_results[0].error
    )
    assert "limit of 5" in runner.result.monitor_results[0].error
    assert "50.0%" in runner.result.monitor_results[0].error

    # Scenario # 8
    data = make_data(
        {
            SPIDERMON_UNWANTED_HTTP_CODES: {
                500: {"max_percentage": 0.5, "max_count": 3},
                400: 2,
            },
        },
    )

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/request_count"] = 10
    data["stats"]["downloader/response_status_count/500"] = 8
    data["stats"]["downloader/response_status_count/400"] = 1
    runner.run(suite, **data)
    assert (
        "Found 8 Responses with status code=500"
        in runner.result.monitor_results[0].error
    )
    assert "limit of 3" in runner.result.monitor_results[0].error

    # Scenario # 9
    data = make_data(
        {
            SPIDERMON_UNWANTED_HTTP_CODES: {
                500: {"max_percentage": 0.99, "max_count": 10},
                400: 2,
            },
        },
    )

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/request_count"] = 10
    data["stats"]["downloader/response_status_count/500"] = 1
    data["stats"]["downloader/response_status_count/400"] = 3
    runner.run(suite, **data)
    assert (
        "Found 3 Responses with status code=400"
        in runner.result.monitor_results[0].error
    )
    assert "limit of 2" in runner.result.monitor_results[0].error

    # Scenario # 10
    data = make_data(
        {
            SPIDERMON_UNWANTED_HTTP_CODES: {
                500: {"max_percentage": 0.5, "max_count": 10},
                400: 2,
            },
        },
    )

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/request_count"] = 10
    data["stats"]["downloader/response_status_count/500"] = 8
    data["stats"]["downloader/response_status_count/400"] = 1
    runner.run(suite, **data)
    assert (
        "Found 8 Responses with status code=500"
        in runner.result.monitor_results[0].error
    )
    assert "limit of 5" in runner.result.monitor_results[0].error
    assert "50.0%" in runner.result.monitor_results[0].error


def test_unwanted_httpcodes_should_pass(make_data):
    """Unwanted HTTP Code should pass if # off responses with error status
    codes is lower than expected
    """
    # Scenario # 1
    data = make_data({SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT: 16})

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/response_status_count/500"] = 16
    data["stats"]["downloader/response_status_count/400"] = 2
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None

    # Scenario # 2
    data = make_data({SPIDERMON_UNWANTED_HTTP_CODES: [400]})

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/response_status_count/400"] = 9
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None

    # Scenario # 3
    data = make_data(
        {
            SPIDERMON_UNWANTED_HTTP_CODES: [500],
            SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT: 15,
        },
    )

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/response_status_count/500"] = 14
    data["stats"]["downloader/response_status_count/400"] = 2
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None

    # Scenario # 4
    data = make_data({SPIDERMON_UNWANTED_HTTP_CODES: {500: 10, 400: 2}})

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/response_status_count/500"] = 8
    data["stats"]["downloader/response_status_count/400"] = 2
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None

    # Scenario # 5
    data = make_data()
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/response_status_count/500"] = 9
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None

    # Scenario # 6
    data = make_data(
        {
            SPIDERMON_UNWANTED_HTTP_CODES: {
                500: {"max_percentage": 0.5},
                400: 2,
            },
        },
    )

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/request_count"] = 10
    data["stats"]["downloader/response_status_count/500"] = 4
    data["stats"]["downloader/response_status_count/400"] = 1
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None

    # Scenario # 7
    data = make_data(
        {
            SPIDERMON_UNWANTED_HTTP_CODES: {
                500: {"max_count": 5, "max_percentage": 0.9},
                400: 2,
            },
        },
    )

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/request_count"] = 10
    data["stats"]["downloader/response_status_count/500"] = 4
    data["stats"]["downloader/response_status_count/400"] = 1
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None

    # Scenario # 8
    data = make_data(
        {
            SPIDERMON_UNWANTED_HTTP_CODES: {
                500: {},
                400: 2,
            },
        },
    )

    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["downloader/request_count"] = 10
    data["stats"]["downloader/response_status_count/500"] = 4
    data["stats"]["downloader/response_status_count/400"] = 1
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None
