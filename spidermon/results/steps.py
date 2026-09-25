import time
from collections import OrderedDict
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from spidermon import settings

from .items import ActionResult, ItemResult, MonitorResult

_I = TypeVar("_I", bound=ItemResult)


class Step(Generic[_I]):
    item_result_class: type[_I]
    successful_statuses: Sequence[str] = []
    error_statuses: Sequence[str] = []

    def __init__(self, name: str) -> None:
        self.name = name
        self._results: OrderedDict[Any, _I] = OrderedDict()
        self.start_time = 0.0
        self.finish_time = 0.0

    @property
    def time_taken(self) -> float:
        return self.finish_time - self.start_time

    @property
    def number_of_items(self) -> int:
        return len(self._results)

    def add_item(self, item: Any) -> _I:
        result = self.item_result_class(item)
        self._results[item] = result
        return result

    def start(self) -> None:
        self.start_time = time.time()

    def finish(self) -> None:
        self.finish_time = time.time()

    def items_for_status(self, status: str) -> list[_I]:
        return [
            result for item, result in self._results.items() if result.status == status
        ]

    def items_for_statuses(self, statuses: Sequence[str]) -> list[_I]:
        items: list[_I] = []
        for status in statuses:
            items += self.items_for_status(status)
        return items

    @property
    def all_items(self) -> list[_I]:
        return list(self._results.values())

    def get_infos(self) -> dict[str, int]:
        raise NotImplementedError

    def __getitem__(self, key: Any) -> _I:
        return self._results[key]

    @property
    def successful_results(self) -> list[_I]:
        results: list[_I] = []
        for successful_status in self.successful_statuses:
            results += self.items_for_status(successful_status)
        return results

    @property
    def error_results(self) -> list[_I]:
        results: list[_I] = []
        for error_status in self.error_statuses:
            results += self.items_for_status(error_status)
        return results

    @property
    def successful(self) -> bool:
        return not self.has_errors

    @property
    def has_errors(self) -> bool:
        return len(self.error_results) > 0


class MonitorStep(Step[MonitorResult]):
    item_result_class = MonitorResult
    successful_statuses = settings.MONITOR.STATUSES.SUCCESSFUL
    error_statuses = settings.MONITOR.STATUSES.ERROR

    def get_infos(self) -> dict[str, int]:
        return {
            "failures": len(self.items_for_status(settings.MONITOR.STATUS.FAILURE)),
            "errors": len(self.items_for_status(settings.MONITOR.STATUS.ERROR)),
            "skipped": len(self.items_for_status(settings.MONITOR.STATUS.SKIPPED)),
            "expected failures": len(
                self.items_for_status(settings.MONITOR.STATUS.EXPECTED_FAILURE),
            ),
            "unexpected successes": len(
                self.items_for_status(settings.MONITOR.STATUS.UNEXPECTED_SUCCESS),
            ),
        }


class ActionsStep(Step[ActionResult]):
    item_result_class = ActionResult
    successful_statuses = settings.ACTION.STATUSES.SUCCESSFUL
    error_statuses = settings.ACTION.STATUSES.ERROR

    def get_infos(self) -> dict[str, int]:
        return {
            "errors": len(self.items_for_status(settings.ACTION.STATUS.ERROR)),
            "skipped": len(self.items_for_status(settings.ACTION.STATUS.SKIPPED)),
        }
