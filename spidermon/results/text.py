from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, TextIO

from spidermon import settings
from spidermon.utils.text import line_title

from .monitor import MonitorResult, actions_step_required, monitors_step_required

if TYPE_CHECKING:
    import unittest

    from _typeshed import OptExcInfo

DOTS = {
    # Monitors
    settings.MONITOR.STATUS.SUCCESS: ".",
    settings.MONITOR.STATUS.ERROR: "E",
    settings.MONITOR.STATUS.FAILURE: "F",
    settings.MONITOR.STATUS.SKIPPED: "s",
    settings.MONITOR.STATUS.EXPECTED_FAILURE: "x",
    settings.MONITOR.STATUS.UNEXPECTED_SUCCESS: "u",
    # Actions
    settings.ACTION.STATUS.SUCCESS: ".",
    settings.ACTION.STATUS.ERROR: "E",
    settings.ACTION.STATUS.SKIPPED: "s",
}


class TextMonitorResult(MonitorResult):
    SEPARATOR_BOLD = "="
    SEPARATOR_LIGHT = "-"
    LINE_LENGTH = 70

    def __init__(self, stream: TextIO = sys.stderr, verbosity: int = 1) -> None:
        super().__init__()
        self.stream = stream
        self.show_all = verbosity > 1
        self.use_dots = verbosity == 1

    def next_step(self) -> None:
        super().next_step()
        self.write_title(self.step.name)

    def finish_step(self) -> None:
        super().finish_step()
        if self.use_dots:
            self.write_line()
        if not self.step.successful:
            self.write_errors()
        self.write_run_footer()
        self.write_step_summary()

    @monitors_step_required
    def startTest(self, test: unittest.TestCase) -> None:
        super().startTest(test)
        self.write_run_start(test)

    @monitors_step_required
    def addSuccess(self, test: unittest.TestCase) -> None:
        super().addSuccess(test)
        self.write_run_result(test)

    @monitors_step_required
    def addError(self, test: unittest.TestCase, error: OptExcInfo) -> None:
        super().addError(test, error)
        self.write_run_result(test)

    @monitors_step_required
    def addFailure(self, test: unittest.TestCase, error: OptExcInfo) -> None:
        super().addFailure(test, error)
        self.write_run_result(test)

    @monitors_step_required
    def addSkip(self, test: unittest.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        self.write_run_result(test, reason)

    @monitors_step_required
    def addExpectedFailure(self, test: unittest.TestCase, error: OptExcInfo) -> None:
        super().addExpectedFailure(test, error)
        self.write_run_result(test)

    @monitors_step_required
    def addUnexpectedSuccess(self, test: unittest.TestCase) -> None:
        super().addUnexpectedSuccess(test)
        self.write_run_result(test)

    @actions_step_required
    def start_action(self, action: Any) -> None:
        super().start_action(action)
        self.write_run_start(action)

    @actions_step_required
    def add_action_success(self, action: Any) -> None:
        super().add_action_success(action)
        self.write_run_result(action)

    @actions_step_required
    def add_action_skip(self, action: Any, reason: str) -> None:
        super().add_action_skip(action, reason)
        self.write_run_result(action, reason)

    @actions_step_required
    def add_action_error(self, action: Any, error: str) -> None:
        super().add_action_error(action, error)
        self.write_run_result(action)

    def write(self, text: str) -> None:
        self.stream.write(text)

    def write_flush(self) -> None:
        self.stream.flush()

    def write_line_light(self) -> None:
        self.write_line(self.SEPARATOR_LIGHT * self.LINE_LENGTH)

    def write_line_bold(self) -> None:
        self.write_line(self.SEPARATOR_BOLD * self.LINE_LENGTH)

    def write_title(self, title: str) -> None:
        self.write_line(line_title(title))

    def write_line(self, text: str | None = None) -> None:
        self.write(f"{text or ''}\n")

    def write_run_status(self, text: str, extra: str | None = None) -> None:
        self.write_line(f"{text}{f' ({extra})' if extra else ''}")

    def write_run_start(self, item: Any) -> None:
        if self.show_all:
            self.write(item.name)
            self.write(" ... ")
            self.write_flush()

    def write_run_result(self, item: Any, extra: str | None = None) -> None:
        if self.show_all:
            self.write_run_status(self.step[item].status, extra)
        elif self.use_dots:
            self.write(DOTS[self.step[item].status])
            self.write_flush()

    def write_run_footer(self) -> None:
        self.write_line_light()
        self.write_line(
            "{count:d} {item_name}{plural_suffix} in {time:.3f}s".format(
                count=self.step.number_of_items,
                item_name=self.step.item_result_class.name,
                plural_suffix="" if self.step.number_of_items == 1 else "s",
                time=self.step.time_taken,
            ),
        )
        self.write_line()

    def write_errors(self) -> None:
        self.write_line()
        for status in self.step.error_statuses:
            for item in self.step.items_for_status(status):
                self.write_line_bold()
                self.write_line(f"{item.status}: {item.item.name}")
                self.write_line_light()
                self.write_line(item.error)
                self.write_line()

    def write_step_summary(self) -> None:
        self.write("OK" if self.step.successful else "FAILED")
        infos = self.step.get_infos()
        if infos and sum(infos.values()):
            self.write_line(
                f" ({', '.join([f'{k}={v}' for k, v in infos.items() if v])})"
            )
        else:
            self.write_line()
        self.write_line()
