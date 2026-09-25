from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, ClassVar

from spidermon.core.suites import MonitorSuite
from spidermon.data import Data
from spidermon.exceptions import InvalidMonitor, InvalidResult
from spidermon.results.monitor import MonitorResult
from spidermon.results.text import TextMonitorResult

if TYPE_CHECKING:
    from typing import TextIO


class MonitorRunner:
    data_immutable_dicts: ClassVar[list[str]] = ["stats"]
    data_default_data: ClassVar[dict[str, Any]] = {"meta": {}}

    def __init__(self) -> None:
        self.suite: MonitorSuite | None = None
        self.result: MonitorResult | None = None
        self.data: Data | None = None

    def run(self, suite: MonitorSuite, **data: Any) -> MonitorResult:
        if not isinstance(suite, MonitorSuite):
            raise InvalidMonitor("Runners must receive a MonitorSuite instance")
        self.suite = suite
        data = dict(self.data_default_data, **data)
        self.data = self.transform_data(**data)
        self.suite.init_data(self.data)
        self.result = self.create_result()
        if not isinstance(self.result, MonitorResult):
            raise InvalidResult("Runners must use a MonitorResult instance")
        return self.run_suite()

    def transform_data(self, **data: Any) -> Data:
        data = data or {}
        new_data_dict: dict[str, Any] = {}
        for attr_name, attr in data.items():
            new_data = Data(attr) if attr_name in self.data_immutable_dicts else attr
            new_data_dict[attr_name] = new_data
        return Data(new_data_dict)

    def run_suite(self) -> MonitorResult:
        assert self.result is not None
        self.result.start()
        self.run_monitors()
        self.run_actions()
        self.result.finish()
        return self.result

    def run_monitors(self) -> None:
        assert self.suite is not None
        assert self.result is not None
        self.result.next_step()
        self.suite(self.result)
        self.result.finish_step()

    def run_actions(self) -> None:
        assert self.suite is not None
        assert self.result is not None
        # Run monitors finished actions
        self.result.next_step()
        self.run_monitors_finished()
        self.result.finish_step()

        # Run monitors passed actions
        self.result.next_step()
        if self.result.monitor_results and self.result.all_monitors_passed:
            self.run_monitors_passed()
        else:
            self.result.skip_all_step_actions(
                actions=self.suite.monitors_passed_actions,
                reason="A Monitor failed",
            )
        self.result.finish_step()

        # Run monitors failed actions
        self.result.next_step()
        if self.result.monitor_results and not self.result.all_monitors_passed:
            self.run_monitors_failed()
        else:
            self.result.skip_all_step_actions(
                actions=self.suite.monitors_failed_actions,
                reason="No Monitors failed",
            )
        self.result.finish_step()

    def run_monitors_finished(self) -> None:
        assert self.suite is not None
        assert self.result is not None
        self.suite.on_monitors_finished(self.result)
        for action in self.suite.monitors_finished_actions:
            action.run(self.result, self.data)

    def run_monitors_passed(self) -> None:
        assert self.suite is not None
        assert self.result is not None
        self.suite.on_monitors_passed(self.result)
        for action in self.suite.monitors_passed_actions:
            action.run(self.result, self.data)

    def run_monitors_failed(self) -> None:
        assert self.suite is not None
        assert self.result is not None
        self.suite.on_monitors_failed(self.result)
        for action in self.suite.monitors_failed_actions:
            action.run(self.result, self.data)

    def create_result(self) -> MonitorResult:
        return MonitorResult()


class TextMonitorRunner(MonitorRunner):
    def __init__(self, stream: TextIO = sys.stderr, verbosity: int = 1) -> None:
        super().__init__()
        self.stream = stream
        self.verbosity = verbosity

    def create_result(self) -> MonitorResult:
        return TextMonitorResult(stream=self.stream, verbosity=self.verbosity)
