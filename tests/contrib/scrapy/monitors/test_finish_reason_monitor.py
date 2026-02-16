import pytest

pytest.importorskip("scrapy")

from spidermon import MonitorSuite
from spidermon.contrib.scrapy.monitors import (
    SPIDERMON_EXPECTED_FINISH_REASONS,
    FinishReasonMonitor,
)


def new_suite():
    return MonitorSuite(monitors=[FinishReasonMonitor])


def test_finished_reason_monitor_should_fail(make_data):
    """FinishedReason should fail when spider finished with unexpected
    reason
    """
    data = make_data()
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["finish_reason"] = "bad_finish"
    runner.run(suite, **data)
    assert (
        'Finished with "bad_finish" the expected reasons'
        in runner.result.monitor_results[0].error
    )


def test_finished_reason_monitor_should_pass(make_data):
    """FinishedReason should succeed when spider finished with expected
    reason
    """
    data = make_data({SPIDERMON_EXPECTED_FINISH_REASONS: "special_reason"})
    runner = data.pop("runner")
    suite = new_suite()
    data["stats"]["finish_reason"] = "special_reason"
    runner.run(suite, **data)
    assert runner.result.monitor_results[0].error is None
