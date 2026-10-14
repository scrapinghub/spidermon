from __future__ import annotations

import io
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from spidermon import MonitorSuite
from spidermon.results import steps
from spidermon.results.text import TextMonitorResult
from spidermon.runners import TextMonitorRunner
from spidermon.utils.text import line_title

from .fixtures.results import (
    AllStatusesMonitor,
    FailingAction,
    PassingMonitor,
    SkippedAction,
    SuccessfulAction,
)

if TYPE_CHECKING:
    from spidermon.core.actions import Action
    from spidermon.core.monitors import Monitor

LIGHT_LINE = "-" * 70
BOLD_LINE = "=" * 70


@pytest.fixture(autouse=True)
def frozen_time(monkeypatch: pytest.MonkeyPatch) -> None:
    # Make step durations, and so the "in 0.000s" footers, deterministic.
    monkeypatch.setattr(steps, "time", SimpleNamespace(time=lambda: 0.0))


def run(
    monitors: list[type[Monitor]],
    verbosity: int = 1,
    finished: list[type[Action]] | None = None,
    passed: list[type[Action]] | None = None,
    failed: list[type[Action]] | None = None,
) -> str:
    stream = io.StringIO()
    suite = MonitorSuite(
        monitors=monitors,
        monitors_finished_actions=finished,
        monitors_passed_actions=passed,
        monitors_failed_actions=failed,
    )
    TextMonitorRunner(stream=stream, verbosity=verbosity).run(suite)
    return stream.getvalue()


def test_passing_run_output() -> None:
    output = run([PassingMonitor], finished=[SuccessfulAction])
    assert output == "\n".join(
        [
            line_title("MONITORS"),
            ".",
            LIGHT_LINE,
            "1 monitor in 0.000s",
            "",
            "OK",
            "",
            line_title("FINISHED ACTIONS"),
            ".",
            LIGHT_LINE,
            "1 action in 0.000s",
            "",
            "OK",
            "",
            line_title("PASSED ACTIONS"),
            "",
            LIGHT_LINE,
            "0 actions in 0.000s",
            "",
            "OK",
            "",
            line_title("FAILED ACTIONS"),
            "",
            LIGHT_LINE,
            "0 actions in 0.000s",
            "",
            "OK",
            "",
            "",
        ]
    )


def test_dots_for_monitor_statuses() -> None:
    lines = run([AllStatusesMonitor]).splitlines()
    assert lines[0] == line_title("MONITORS")
    # success, failure, error, skipped, expected failure, unexpected success
    assert lines[1] == ".FEsxu"
    assert "6 monitors in 0.000s" in lines
    assert (
        "FAILED (failures=1, errors=1, skipped=1, expected failures=1, "
        "unexpected successes=1)"
    ) in lines


def test_dots_for_action_statuses() -> None:
    lines = run(
        [PassingMonitor], finished=[SuccessfulAction, SkippedAction, FailingAction]
    ).splitlines()
    title = lines.index(line_title("FINISHED ACTIONS"))
    assert lines[title + 1] == ".sE"
    assert "3 actions in 0.000s" in lines
    assert "FAILED (errors=1, skipped=1)" in lines


def test_verbose_output() -> None:
    output = run(
        [AllStatusesMonitor],
        verbosity=2,
        finished=[SuccessfulAction, SkippedAction, FailingAction],
    )
    lines = output.splitlines()
    assert lines[1:7] == [
        "AllStatusesMonitor/test_a_success ... OK",
        "AllStatusesMonitor/test_b_failure ... FAIL",
        "AllStatusesMonitor/test_c_error ... ERROR",
        "AllStatusesMonitor/test_d_skipped ... SKIPPED (not today)",
        "AllStatusesMonitor/test_e_expected_failure ... EXPECTED FAILURE",
        "AllStatusesMonitor/test_f_unexpected_success ... UNEXPECTED SUCCESS",
    ]
    title = lines.index(line_title("FINISHED ACTIONS"))
    assert lines[title + 1 : title + 4] == [
        "SuccessfulAction ... OK",
        "SkippedAction ... SKIPPED (nothing to do)",
        "FailingAction ... ERROR",
    ]
    assert "." not in lines
    assert ".FEsxu" not in output


def test_quiet_output() -> None:
    output = run([AllStatusesMonitor], verbosity=0, finished=[SuccessfulAction])
    lines = output.splitlines()
    assert ".FEsxu" not in output
    assert "AllStatusesMonitor/test_a_success ... OK" not in lines
    # Without dots there is no line break between the title and the errors.
    assert lines[:3] == [line_title("MONITORS"), "", BOLD_LINE]
    title = lines.index(line_title("FINISHED ACTIONS"))
    assert lines[title + 1 : title + 3] == [LIGHT_LINE, "1 action in 0.000s"]


def test_errors_are_written_for_failed_steps() -> None:
    output = run([AllStatusesMonitor], finished=[FailingAction])
    failure = (
        f"{BOLD_LINE}\nFAIL: AllStatusesMonitor/test_b_failure\n{LIGHT_LINE}\n"
        "Traceback (most recent call last):\n"
    )
    error = (
        f"{BOLD_LINE}\nERROR: AllStatusesMonitor/test_c_error\n{LIGHT_LINE}\n"
        "Traceback (most recent call last):\n"
    )
    action_error = (
        f"{BOLD_LINE}\nERROR: FailingAction\n{LIGHT_LINE}\n"
        "Traceback (most recent call last):\n"
    )
    assert failure in output
    assert "AssertionError: boom\n" in output
    assert error in output
    assert "ValueError: kaboom\n" in output
    assert action_error in output
    assert "ValueError: action boom\n" in output
    # Only failures and errors are detailed.
    assert "SKIPPED: " not in output
    assert "EXPECTED FAILURE: " not in output
    assert output.index(failure) < output.index(error) < output.index(action_error)


def test_errors_are_not_written_for_successful_steps() -> None:
    output = run([PassingMonitor], finished=[SuccessfulAction, SkippedAction])
    assert BOLD_LINE not in output
    assert "OK (skipped=1)" in output.splitlines()


def test_skipped_step_actions_are_counted_but_not_written() -> None:
    lines = run(
        [AllStatusesMonitor], verbosity=2, passed=[SuccessfulAction]
    ).splitlines()
    title = lines.index(line_title("PASSED ACTIONS"))
    assert lines[title + 1 : title + 5] == [
        LIGHT_LINE,
        "1 action in 0.000s",
        "",
        "OK (skipped=1)",
    ]


def test_monitor_methods_require_monitors_step() -> None:
    result = TextMonitorResult(stream=io.StringIO())
    result.next_step()
    result.next_step()
    monitor = PassingMonitor("test_pass")
    with pytest.raises(ValueError):  # noqa: PT011
        result.startTest(monitor)
    with pytest.raises(ValueError):  # noqa: PT011
        result.addSuccess(monitor)


def test_action_methods_require_actions_step() -> None:
    result = TextMonitorResult(stream=io.StringIO())
    result.next_step()
    action = SuccessfulAction()
    with pytest.raises(ValueError):  # noqa: PT011
        result.start_action(action)
    with pytest.raises(ValueError):  # noqa: PT011
        result.add_action_success(action)
