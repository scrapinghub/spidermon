import logging

import pytest

pytest.importorskip("scrapy")

from scrapy import Spider

from spidermon import Monitor, MonitorSuite, monitors
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner
from spidermon.core.actions import Action


class LowLevelFailingMonitor(Monitor):
    @monitors.level.low
    def test_fails(self) -> None:
        self.fail("low level failure")


class DefaultLevelFailingMonitor(Monitor):
    def test_fails(self) -> None:
        self.fail("default level failure")


class PassingMonitor(Monitor):
    def test_passes(self) -> None:
        pass


class FailingAction(Action):
    def run_action(self) -> None:
        raise RuntimeError("action failure")


def _run(suite: MonitorSuite, caplog: pytest.LogCaptureFixture) -> dict[str, int]:
    with caplog.at_level(logging.DEBUG):
        SpiderMonitorRunner(spider=Spider("dummy")).run(suite, stats={})
    return {
        text: record.levelno
        for record in caplog.records
        for text in ("low level failure", "default level failure", "action failure")
        if text in record.getMessage()
    }


def test_write_errors_uses_monitor_level(caplog: pytest.LogCaptureFixture) -> None:
    suite = MonitorSuite(monitors=[LowLevelFailingMonitor, DefaultLevelFailingMonitor])
    assert _run(suite, caplog) == {
        "low level failure": logging.WARNING,
        "default level failure": logging.ERROR,
    }


def test_write_errors_logs_action_errors_as_errors(
    caplog: pytest.LogCaptureFixture,
) -> None:
    suite = MonitorSuite(
        monitors=[PassingMonitor],
        monitors_finished_actions=[FailingAction],
    )
    assert _run(suite, caplog) == {"action failure": logging.ERROR}
