from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from spidermon.results.monitor import (
    MonitorResult,
    actions_step_required,
    monitors_step_required,
)
from spidermon.runners import MonitorRunner
from spidermon.utils.text import Message, line, line_title

if TYPE_CHECKING:
    import unittest

    from _typeshed import OptExcInfo
    from scrapy import Spider

LOG_MESSAGE_HEADER = "Spidermon"


class SpiderMonitorResult(MonitorResult):
    def __init__(self, spider: Spider) -> None:
        super().__init__()
        self.spider = spider

    def next_step(self) -> None:
        super().next_step()
        self.write_title()

    def finish_step(self) -> None:
        super().finish_step()
        self.log_info(line())
        if not self.step.successful:
            self.write_errors()
        self.write_run_footer()
        self.write_step_summary()

    @monitors_step_required
    def addSuccess(self, test: unittest.TestCase) -> None:
        super().addSuccess(test)
        self.write_item_result(test)

    @monitors_step_required
    def addError(self, test: unittest.TestCase, error: OptExcInfo) -> None:
        super().addError(test, error)
        self.write_item_result(test)

    @monitors_step_required
    def addFailure(self, test: unittest.TestCase, error: OptExcInfo) -> None:
        super().addFailure(test, error)
        self.write_item_result(test)

    @monitors_step_required
    def addSkip(self, test: unittest.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        self.write_item_result(test, reason)

    @monitors_step_required
    def addExpectedFailure(self, test: unittest.TestCase, error: OptExcInfo) -> None:
        super().addExpectedFailure(test, error)
        self.write_item_result(test)

    @monitors_step_required
    def addUnexpectedSuccess(self, test: unittest.TestCase) -> None:
        super().addUnexpectedSuccess(test)
        self.write_item_result(test)

    @actions_step_required
    def add_action_success(self, action: Any) -> None:
        super().add_action_success(action)
        self.write_item_result(action)

    @actions_step_required
    def add_action_skip(self, action: Any, reason: str) -> None:
        super().add_action_skip(action, reason)
        self.write_item_result(action, reason)

    @actions_step_required
    def add_action_error(self, action: Any, error: str) -> None:
        super().add_action_error(action, error)
        self.write_item_result(action)

    def write_title(self) -> None:
        self.log_info(line_title(self.step.name))

    def write_item_result(self, item: Any, extra: str | None = None) -> None:
        self.log_info(
            f"{item.name}... {self.step[item].status}{f' ({extra})' if extra else ''}",
        )

    def write_run_footer(self) -> None:
        self.log_info(
            "{count:d} {item_name}{plural_suffix} in {time:.3f}s".format(
                count=self.step.number_of_items,
                item_name=self.step.item_result_class.name,
                plural_suffix="" if self.step.number_of_items == 1 else "s",
                time=self.step.time_taken,
            ),
        )

    def write_step_summary(self) -> None:
        summary = "OK" if self.step.successful else "FAILED"
        infos = self.step.get_infos()
        if infos and sum(infos.values()):
            summary += f" ({', '.join([f'{k}={v}' for k, v in infos.items() if v])})"
        self.log_info(summary)

    def write_errors(self) -> None:
        for status in self.step.error_statuses:
            for item in self.step.items_for_status(status):
                msg = Message()
                msg.write_line()
                msg.write_bold_separator()
                msg.write_line(f"{item.status}: {item.item.name}")
                msg.write_light_separator()
                assert item.error is not None
                msg.write(item.error)
                self.log(msg, level=getattr(item.item, "level", logging.ERROR))

    def log_info(self, msg: object) -> None:
        self.log(msg, level=logging.INFO)

    def log(self, msg: object, level: int = logging.DEBUG) -> None:
        self.spider.logger.log(level, f"[{LOG_MESSAGE_HEADER}] {msg}")


class SpiderMonitorRunner(MonitorRunner):
    def __init__(self, spider: Spider) -> None:
        super().__init__()
        self.spider = spider

    def create_result(self) -> SpiderMonitorResult:
        return SpiderMonitorResult(self.spider)
