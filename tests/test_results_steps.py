from __future__ import annotations

from types import SimpleNamespace

import pytest

from spidermon import settings
from spidermon.results import steps
from spidermon.results.items import ActionResult, ItemResult, MonitorResult
from spidermon.results.steps import ActionsStep, MonitorStep, Step

MONITOR = settings.MONITOR.STATUS
ACTION = settings.ACTION.STATUS


def monitor_step(*statuses: str) -> MonitorStep:
    step = MonitorStep(settings.STEPS.MONITORS)
    for index, status in enumerate(statuses):
        step.add_item(f"monitor-{index}").status = status
    return step


def actions_step(*statuses: str) -> ActionsStep:
    step = ActionsStep(settings.STEPS.MONITORS_FINISHED)
    for index, status in enumerate(statuses):
        step.add_item(f"action-{index}").status = status
    return step


def test_item_results() -> None:
    item = ItemResult("item")
    assert item.item == "item"
    assert item.status == settings.UNDEFINED_STATUS
    assert item.error is None
    assert item.reason is None
    assert item.id == id(item)

    monitor = MonitorResult("monitor")
    assert monitor.name == "monitor"
    assert monitor.monitor == "monitor"
    assert monitor.status == settings.MONITOR.STATUSES.DEFAULT

    action = ActionResult("action")
    assert action.name == "action"
    assert action.action == "action"
    assert action.status == settings.ACTION.STATUSES.DEFAULT


def test_add_item() -> None:
    step = MonitorStep(settings.STEPS.MONITORS)
    assert step.number_of_items == 0
    result = step.add_item("monitor")
    assert isinstance(result, MonitorResult)
    assert step["monitor"] is result
    assert step.all_items == [result]
    assert step.number_of_items == 1
    assert isinstance(ActionsStep("actions").add_item("action"), ActionResult)


def test_time_taken(monkeypatch: pytest.MonkeyPatch) -> None:
    step = MonitorStep(settings.STEPS.MONITORS)
    assert step.time_taken == 0
    monkeypatch.setattr(steps, "time", SimpleNamespace(time=lambda: 10.0))
    step.start()
    monkeypatch.setattr(steps, "time", SimpleNamespace(time=lambda: 12.5))
    step.finish()
    assert step.time_taken == 2.5


def test_items_for_statuses() -> None:
    step = monitor_step(MONITOR.SUCCESS, MONITOR.ERROR, MONITOR.SUCCESS)
    items = step.all_items
    assert step.items_for_status(MONITOR.SUCCESS) == [items[0], items[2]]
    assert step.items_for_status(MONITOR.SKIPPED) == []
    assert step.items_for_statuses([MONITOR.ERROR, MONITOR.SUCCESS]) == [
        items[1],
        items[0],
        items[2],
    ]
    assert step.items_for_statuses([]) == []


def test_monitor_step_results() -> None:
    step = monitor_step(
        MONITOR.SUCCESS,
        MONITOR.FAILURE,
        MONITOR.ERROR,
        MONITOR.SKIPPED,
        MONITOR.EXPECTED_FAILURE,
        MONITOR.UNEXPECTED_SUCCESS,
    )
    items = step.all_items
    assert step.successful_results == [items[0], items[3], items[4], items[5]]
    assert step.error_results == [items[1], items[2]]
    assert step.has_errors
    assert not step.successful
    assert step.get_infos() == {
        "failures": 1,
        "errors": 1,
        "skipped": 1,
        "expected failures": 1,
        "unexpected successes": 1,
    }


def test_successful_monitor_step() -> None:
    step = monitor_step(MONITOR.SUCCESS, MONITOR.SKIPPED)
    assert not step.has_errors
    assert step.successful
    assert step.get_infos() == {
        "failures": 0,
        "errors": 0,
        "skipped": 1,
        "expected failures": 0,
        "unexpected successes": 0,
    }


def test_actions_step_results() -> None:
    step = actions_step(ACTION.SUCCESS, ACTION.ERROR, ACTION.SKIPPED)
    items = step.all_items
    assert step.successful_results == [items[0], items[2]]
    assert step.error_results == [items[1]]
    assert not step.successful
    assert step.get_infos() == {"errors": 1, "skipped": 1}


def test_empty_step_is_successful() -> None:
    assert monitor_step().successful
    assert actions_step().successful
    assert actions_step().get_infos() == {"errors": 0, "skipped": 0}


def test_base_step_has_no_infos() -> None:
    with pytest.raises(NotImplementedError):
        Step("step").get_infos()
