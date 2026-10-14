from __future__ import annotations

import unittest
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Concatenate, ParamSpec, TypeVar

from spidermon import settings

from .steps import ActionsStep, MonitorStep, Step

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence

    from _typeshed import OptExcInfo

    from .items import ActionResult
    from .items import MonitorResult as MonitorItemResult

_P = ParamSpec("_P")
_T = TypeVar("_T")
_R = TypeVar("_R", bound="MonitorResult")


def step_required_decorator(
    allowed_steps: Sequence[str],
) -> Callable[[Callable[Concatenate[_R, _P], _T]], Callable[Concatenate[_R, _P], _T]]:
    def _step_required_decorator(
        fn: Callable[Concatenate[_R, _P], _T],
    ) -> Callable[Concatenate[_R, _P], _T]:
        def decorator(self: _R, /, *args: _P.args, **kwargs: _P.kwargs) -> _T:
            if self.step.name not in allowed_steps:
                raise ValueError  # TO-DO
            return fn(self, *args, **kwargs)

        return decorator

    return _step_required_decorator


monitors_step_required = step_required_decorator(settings.STEPS.MONITOR_RELATED)
actions_step_required = step_required_decorator(settings.STEPS.ACTION_RELATED)


class MonitorResult(unittest.TestResult):
    if TYPE_CHECKING:

        def _exc_info_to_string(
            self, err: OptExcInfo, test: unittest.TestCase
        ) -> str: ...

    def __init__(self) -> None:
        super().__init__()
        self._steps: OrderedDict[str, Step[Any]] = OrderedDict(
            [(step, self._get_step_class(step)(step)) for step in settings.STEPS.ALL],
        )
        self._current_step: Step[Any] | None = None

    @property
    def all_monitors_passed(self) -> bool:
        return self._step_monitors.successful

    @property
    def monitor_results(self) -> list[MonitorItemResult]:
        return self._step_monitors.all_items

    @property
    def monitors_passed_results(self) -> list[MonitorItemResult]:
        return self._step_monitors.items_for_statuses(
            settings.MONITOR.STATUSES.SUCCESSFUL,
        )

    @property
    def monitors_failed_results(self) -> list[MonitorItemResult]:
        return self._step_monitors.items_for_statuses(settings.MONITOR.STATUSES.ERROR)

    @property
    def monitors_finished_action_results(self) -> list[ActionResult]:
        return self._step_monitors_finished.all_items

    @property
    def monitors_passed_action_results(self) -> list[ActionResult]:
        return self._step_monitors_passed.all_items

    @property
    def monitors_failed_action_results(self) -> list[ActionResult]:
        return self._step_monitors_failed.all_items

    @property
    def step(self) -> Step[Any]:
        assert self._current_step is not None
        return self._current_step

    def start(self) -> None:
        pass

    def finish(self) -> None:
        pass

    def next_step(self) -> None:
        index = (
            0
            if not self._current_step
            else list(self._steps.keys()).index(self.step.name) + 1
        )
        self._current_step = list(self._steps.items())[index][1]
        self.step.start()

    def finish_step(self) -> None:
        self.step.finish()

    @monitors_step_required
    def startTest(self, test: unittest.TestCase) -> None:
        super().startTest(test)
        self.step.add_item(test)

    @monitors_step_required
    def addSuccess(self, test: unittest.TestCase) -> None:
        super().addSuccess(test)
        self.step[test].status = settings.MONITOR.STATUS.SUCCESS

    @monitors_step_required
    def addError(self, test: unittest.TestCase, error: OptExcInfo) -> None:
        super().addError(test, error)
        self.step[test].status = settings.MONITOR.STATUS.ERROR
        self.step[test].error = self._exc_info_to_string(error, test)

    @monitors_step_required
    def addFailure(self, test: unittest.TestCase, error: OptExcInfo) -> None:
        super().addFailure(test, error)
        self.step[test].status = settings.MONITOR.STATUS.FAILURE
        self.step[test].error = self._exc_info_to_string(error, test)
        self.step[test].reason = str(error[1])

    @monitors_step_required
    def addSkip(self, test: unittest.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        self.step[test].status = settings.MONITOR.STATUS.SKIPPED
        self.step[test].reason = reason

    @monitors_step_required
    def addExpectedFailure(self, test: unittest.TestCase, error: OptExcInfo) -> None:
        super().addExpectedFailure(test, error)
        self.step[test].status = settings.MONITOR.STATUS.EXPECTED_FAILURE
        self.step[test].error = self._exc_info_to_string(error, test)

    @monitors_step_required
    def addUnexpectedSuccess(self, test: unittest.TestCase) -> None:
        super().addUnexpectedSuccess(test)
        self.step[test].status = settings.MONITOR.STATUS.UNEXPECTED_SUCCESS

    @actions_step_required
    def start_action(self, action: Any) -> None:
        self.step.add_item(action)

    @actions_step_required
    def add_action_success(self, action: Any) -> None:
        self.step[action].status = settings.ACTION.STATUS.SUCCESS

    @actions_step_required
    def add_action_skip(self, action: Any, reason: str) -> None:
        self.step[action].status = settings.ACTION.STATUS.SKIPPED
        self.step[action].reason = reason

    @actions_step_required
    def add_action_error(self, action: Any, error: str) -> None:
        self.step[action].status = settings.ACTION.STATUS.ERROR
        self.step[action].error = error

    @actions_step_required
    def skip_all_step_actions(self, actions: Iterable[Any], reason: str) -> None:
        for action in actions:
            result = self.step.add_item(action)
            result.status = settings.ACTION.STATUS.SKIPPED
            result.reason = reason

    @property
    def _step_monitors(self) -> Step[MonitorItemResult]:
        return self._steps[settings.STEPS.MONITORS]

    @property
    def _step_monitors_finished(self) -> Step[ActionResult]:
        return self._steps[settings.STEPS.MONITORS_FINISHED]

    @property
    def _step_monitors_passed(self) -> Step[ActionResult]:
        return self._steps[settings.STEPS.MONITORS_PASSED]

    @property
    def _step_monitors_failed(self) -> Step[ActionResult]:
        return self._steps[settings.STEPS.MONITORS_FAILED]

    def _get_step_class(self, step: str) -> type[Step[Any]]:
        return MonitorStep if step in settings.STEPS.MONITOR_RELATED else ActionsStep
