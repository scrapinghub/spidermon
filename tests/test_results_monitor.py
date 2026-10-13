from __future__ import annotations

import pytest

from spidermon import MonitorSuite, settings
from spidermon.results.monitor import MonitorResult
from spidermon.results.steps import ActionsStep, MonitorStep
from spidermon.runners import MonitorRunner

from .fixtures.results import (
    AllStatusesMonitor,
    FailingAction,
    PassingMonitor,
    SkippedAction,
    SuccessfulAction,
)

ALL_ACTIONS = [SuccessfulAction, SkippedAction, FailingAction]
NO_EXC_INFO = (None, None, None)


def run(monitor: type[PassingMonitor | AllStatusesMonitor]) -> MonitorResult:
    suite = MonitorSuite(
        monitors=[monitor],
        monitors_finished_actions=ALL_ACTIONS,
        monitors_passed_actions=ALL_ACTIONS,
        monitors_failed_actions=ALL_ACTIONS,
    )
    result = MonitorRunner().run(suite)
    assert isinstance(result, MonitorResult)
    return result


def test_steps_follow_settings_order() -> None:
    result = MonitorResult()
    step_names = []
    for _ in settings.STEPS.ALL:
        result.next_step()
        assert result.step.start_time > 0
        result.finish_step()
        assert result.step.finish_time >= result.step.start_time
        step_names.append(result.step.name)
    assert step_names == list(settings.STEPS.ALL)


@pytest.mark.parametrize(
    ("step", "step_class"),
    [
        (settings.STEPS.MONITORS, MonitorStep),
        (settings.STEPS.MONITORS_FINISHED, ActionsStep),
        (settings.STEPS.MONITORS_PASSED, ActionsStep),
        (settings.STEPS.MONITORS_FAILED, ActionsStep),
    ],
)
def test_step_classes(step: str, step_class: type[MonitorStep | ActionsStep]) -> None:
    result = MonitorResult()
    result.next_step()
    while result.step.name != step:
        result.next_step()
    assert type(result.step) is step_class


def test_monitor_statuses() -> None:
    result = run(AllStatusesMonitor)
    statuses = {r.monitor.method_name: r for r in result.monitor_results}
    assert {name: r.status for name, r in statuses.items()} == {
        "test_a_success": settings.MONITOR.STATUS.SUCCESS,
        "test_b_failure": settings.MONITOR.STATUS.FAILURE,
        "test_c_error": settings.MONITOR.STATUS.ERROR,
        "test_d_skipped": settings.MONITOR.STATUS.SKIPPED,
        "test_e_expected_failure": settings.MONITOR.STATUS.EXPECTED_FAILURE,
        "test_f_unexpected_success": settings.MONITOR.STATUS.UNEXPECTED_SUCCESS,
    }

    assert statuses["test_a_success"].error is None
    assert statuses["test_a_success"].reason is None
    assert "AssertionError: boom" in str(statuses["test_b_failure"].error)
    assert statuses["test_b_failure"].reason == "boom"
    assert "ValueError: kaboom" in str(statuses["test_c_error"].error)
    assert statuses["test_c_error"].reason is None
    assert statuses["test_d_skipped"].reason == "not today"
    assert "AssertionError: expected" in str(statuses["test_e_expected_failure"].error)
    assert statuses["test_f_unexpected_success"].error is None


def test_monitor_statuses_reach_unittest_result() -> None:
    result = run(AllStatusesMonitor)
    assert result.testsRun == 6
    assert len(result.failures) == 1
    assert len(result.errors) == 1
    assert len(result.skipped) == 1
    assert len(result.expectedFailures) == 1
    assert len(result.unexpectedSuccesses) == 1
    assert not result.wasSuccessful()


def test_monitor_result_groups() -> None:
    result = run(AllStatusesMonitor)
    assert not result.all_monitors_passed
    assert len(result.monitor_results) == 6
    assert [r.monitor.method_name for r in result.monitors_passed_results] == [
        "test_a_success",
        "test_d_skipped",
        "test_e_expected_failure",
        "test_f_unexpected_success",
    ]
    assert [r.monitor.method_name for r in result.monitors_failed_results] == [
        "test_b_failure",
        "test_c_error",
    ]


def test_action_statuses_when_monitors_fail() -> None:
    result = run(AllStatusesMonitor)

    finished = result.monitors_finished_action_results
    assert [type(r.action) for r in finished] == ALL_ACTIONS
    assert [r.status for r in finished] == [
        settings.ACTION.STATUS.SUCCESS,
        settings.ACTION.STATUS.SKIPPED,
        settings.ACTION.STATUS.ERROR,
    ]
    assert finished[0].reason is None
    assert finished[0].error is None
    assert finished[1].reason == "nothing to do"
    assert "ValueError: action boom" in str(finished[2].error)

    passed = result.monitors_passed_action_results
    assert [type(r.action) for r in passed] == ALL_ACTIONS
    assert {r.status for r in passed} == {settings.ACTION.STATUS.SKIPPED}
    assert {r.reason for r in passed} == {"A Monitor failed"}

    failed = result.monitors_failed_action_results
    assert [r.status for r in failed] == [r.status for r in finished]


def test_action_statuses_when_monitors_pass() -> None:
    result = run(PassingMonitor)
    assert result.all_monitors_passed
    assert [r.monitor.method_name for r in result.monitors_passed_results] == [
        "test_pass"
    ]
    assert result.monitors_failed_results == []

    passed = result.monitors_passed_action_results
    assert [r.status for r in passed] == [
        settings.ACTION.STATUS.SUCCESS,
        settings.ACTION.STATUS.SKIPPED,
        settings.ACTION.STATUS.ERROR,
    ]

    failed = result.monitors_failed_action_results
    assert {r.status for r in failed} == {settings.ACTION.STATUS.SKIPPED}
    assert {r.reason for r in failed} == {"No Monitors failed"}


@pytest.mark.parametrize("step", settings.STEPS.ACTION_RELATED)
@pytest.mark.parametrize(
    ("method", "args"),
    [
        ("startTest", ()),
        ("addSuccess", ()),
        ("addError", (NO_EXC_INFO,)),
        ("addFailure", (NO_EXC_INFO,)),
        ("addSkip", ("reason",)),
        ("addExpectedFailure", (NO_EXC_INFO,)),
        ("addUnexpectedSuccess", ()),
    ],
)
def test_monitor_methods_require_monitors_step(
    step: str, method: str, args: tuple[object, ...]
) -> None:
    result = MonitorResult()
    result.next_step()
    while result.step.name != step:
        result.next_step()
    with pytest.raises(ValueError):  # noqa: PT011
        getattr(result, method)(PassingMonitor("test_pass"), *args)
    assert result.step.number_of_items == 0
    assert result.testsRun == 0


@pytest.mark.parametrize(
    ("method", "args"),
    [
        ("start_action", ()),
        ("add_action_success", ()),
        ("add_action_skip", ("reason",)),
        ("add_action_error", ("error",)),
    ],
)
def test_action_methods_require_actions_step(
    method: str, args: tuple[object, ...]
) -> None:
    result = MonitorResult()
    result.next_step()
    with pytest.raises(ValueError):  # noqa: PT011
        getattr(result, method)(SuccessfulAction(), *args)
    assert result.step.number_of_items == 0


def test_skip_all_step_actions_requires_actions_step() -> None:
    result = MonitorResult()
    result.next_step()
    with pytest.raises(ValueError):  # noqa: PT011
        result.skip_all_step_actions([SuccessfulAction()], "reason")
    assert result.step.number_of_items == 0
