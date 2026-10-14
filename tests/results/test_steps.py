from spidermon import settings
from spidermon.results.steps import ActionsStep, MonitorStep


def test_items_for_statuses() -> None:
    step = MonitorStep("monitors")
    failure = step.add_item("failure")
    failure.status = settings.MONITOR.STATUS.FAILURE
    error = step.add_item("error")
    error.status = settings.MONITOR.STATUS.ERROR
    step.add_item("success").status = settings.MONITOR.STATUS.SUCCESS
    assert step.items_for_statuses(
        [settings.MONITOR.STATUS.FAILURE, settings.MONITOR.STATUS.ERROR]
    ) == [failure, error]


def test_successful_results() -> None:
    step = ActionsStep("actions")
    success = step.add_item("success")
    success.status = settings.ACTION.STATUS.SUCCESS
    skipped = step.add_item("skipped")
    skipped.status = settings.ACTION.STATUS.SKIPPED
    step.add_item("error").status = settings.ACTION.STATUS.ERROR
    assert step.successful_results == [success, skipped]
