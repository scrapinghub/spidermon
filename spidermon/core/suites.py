from __future__ import annotations

import collections
import logging
from typing import TYPE_CHECKING, Any, ClassVar, NoReturn, cast
from unittest import TestSuite

from spidermon import settings
from spidermon.exceptions import InvalidMonitorIterable, NotAllowedMethod

from .factories import ActionFactory, MonitorFactory
from .monitors import Monitor
from .options import MonitorOptions, MonitorOptionsMetaclass

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Sequence

    from scrapy.crawler import Crawler

    from spidermon.data import Data
    from spidermon.results.monitor import MonitorResult

    from .actions import Action


class MonitorSuite(TestSuite, metaclass=MonitorOptionsMetaclass):
    options: ClassVar[MonitorOptions]
    monitors: ClassVar[
        Sequence[
            type[MonitorSuite | Monitor] | tuple[str, type[MonitorSuite | Monitor]]
        ]
    ] = []
    monitors_finished_actions: list[Any] = []  # noqa: RUF012
    monitors_passed_actions: list[Any] = []  # noqa: RUF012
    monitors_failed_actions: list[Any] = []  # noqa: RUF012

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        name: str | None = None,
        monitors: Iterable[Any] | None = None,
        monitors_finished_actions: Iterable[type[Action] | Action] | None = None,
        monitors_passed_actions: Iterable[type[Action] | Action] | None = None,
        monitors_failed_actions: Iterable[type[Action] | Action] | None = None,
        order: int | None = None,
        crawler: Crawler | None = None,
    ) -> None:
        self._tests = []
        self._removed_tests = 0
        self._name = name
        self._parent: MonitorSuite | None = None
        self._order = order
        self._crawler = crawler

        self.add_monitors(self.monitors)
        self.add_monitors(monitors or [])

        declarative_monitors_finished_actions = self.monitors_finished_actions
        self.monitors_finished_actions = []
        self.add_monitors_finished_actions(declarative_monitors_finished_actions)
        self.add_monitors_finished_actions(monitors_finished_actions or [])

        declarative_monitors_passed_actions = self.monitors_passed_actions
        self.monitors_passed_actions = []
        self.add_monitors_passed_actions(declarative_monitors_passed_actions)
        self.add_monitors_passed_actions(monitors_passed_actions or [])

        declarative_monitors_failed_actions = self.monitors_failed_actions
        self.monitors_failed_actions = []
        self.add_monitors_failed_actions(declarative_monitors_failed_actions)
        self.add_monitors_failed_actions(monitors_failed_actions or [])

    @property
    def name(self) -> str:
        return self._name or self.options.name or self.__class__.__name__

    @property
    def level(self) -> int:
        return self.options.level or self.parent_level

    @property
    def parent_level(self) -> int:
        if self.parent:
            return self.parent.level
        return settings.MONITOR.LEVELS.DEFAULT

    @property
    def full_name(self) -> str:
        parts = []
        if self.parent and self.parent.full_name:
            parts.append(self.parent.full_name)
        if self.have_custom_name:
            parts.append(self.name)
        return "/".join(parts)

    @property
    def have_custom_name(self) -> str | None:
        return self._name or self.options.name

    @property
    def description(self) -> str:
        return (
            self.options.description
            or self.__class__.__doc__
            or settings.MONITOR.DEFAULT_DESCRIPTION
        )

    @property
    def parent(self) -> MonitorSuite | None:
        return self._parent

    @property
    def order(self) -> int:
        return self._order if self._order is not None else None or self.options.order

    @property
    def number_of_monitors(self) -> int:
        return sum(
            [
                1 if isinstance(monitor, Monitor) else monitor.number_of_monitors
                for monitor in self
            ],
        )

    @property
    def all_monitors(self) -> list[Monitor]:
        monitors: list[Monitor] = []
        for monitor in self:
            if isinstance(monitor, Monitor):
                monitors += [monitor]
            else:
                monitors += monitor.all_monitors
        return monitors

    def set_parent(self, parent: MonitorSuite) -> None:
        self._parent = parent

    def init_data(self, data: Data) -> None:
        for test in self:
            test.init_data(data)

    def add_monitors(self, monitors: Iterable[Any]) -> None:
        if not isinstance(monitors, collections.abc.Iterable):
            raise InvalidMonitorIterable("Monitors definition is not iterable")
        for m in monitors:
            self.add_monitor(m)

    def add_monitor(self, monitor: object, name: str | None = None) -> None:
        monitor = MonitorFactory.load_monitor(monitor, name)
        monitor.set_parent(self)
        super().addTest(monitor)
        self._reorder_tests()

    def add_monitors_finished_actions(
        self,
        actions: Iterable[type[Action] | Action],
    ) -> None:
        for action in actions:
            self.add_monitors_finished_action(action)

    def add_monitors_finished_action(self, action: type[Action] | Action) -> None:
        self._add_action(action, self.monitors_finished_actions)

    def add_monitors_passed_actions(
        self,
        actions: Iterable[type[Action] | Action],
    ) -> None:
        for action in actions:
            self.add_monitors_passed_action(action)

    def add_monitors_passed_action(self, action: type[Action] | Action) -> None:
        self._add_action(action, self.monitors_passed_actions)

    def add_monitors_failed_actions(
        self,
        actions: Iterable[type[Action] | Action],
    ) -> None:
        for action in actions:
            self.add_monitors_failed_action(action)

    def add_monitors_failed_action(self, action: type[Action] | Action) -> None:
        self._add_action(action, self.monitors_failed_actions)

    def _add_action(
        self,
        action: type[Action] | Action,
        target_actions_list: list[Action],
    ) -> None:
        action = ActionFactory.load_action(action, crawler=self._crawler)
        target_actions_list.append(action)

    def debug_tree(self, level: int = 0) -> str:
        s = level * "\t" + repr(self) + "\n"
        for test in self:
            s += test.debug_tree(level=level + 1)
        return s

    def debug_monitors(
        self,
        show_monitor: bool = True,
        show_method: bool = True,
        show_level: bool = True,
        show_order: bool = False,
        show_description: bool = True,
    ) -> str:
        def debug_attribute(condition: bool, name: str, value: object) -> str:
            return f"{name:>12}: {value!s}\n" if condition else ""

        s = "-" * 80 + "\n"
        for t in self.all_monitors:
            s += debug_attribute(show_monitor, "MONITOR", t.monitor_full_name)
            s += debug_attribute(show_method, "METHOD", t.method_name)
            s += debug_attribute(show_level, "LEVEL", logging.getLevelName(t.level))
            s += debug_attribute(show_order, "ORDER", t.order)
            s += debug_attribute(
                show_description,
                "DESCRIPTION",
                t.method_description or "...",
            )
            s += "-" * 80 + "\n"
        return s

    def _reorder_tests(self) -> None:
        self._tests = sorted(
            self._tests,
            key=lambda x: cast("Monitor | MonitorSuite", x).order,
            reverse=False,
        )

    def __repr__(self) -> str:
        return f"<SUITE:{self.name}[{len(self._tests)},{self.number_of_monitors}] at {hex(id(self))}>"

    def __str__(self) -> str:
        return self.name

    def __not_allowed_method(self, *args: Any, **kwargs: Any) -> NoReturn:
        raise NotAllowedMethod

    addTest = __not_allowed_method
    addTests = __not_allowed_method

    if TYPE_CHECKING:

        def __iter__(self) -> Iterator[Monitor | MonitorSuite]: ...

    def on_monitors_finished(self, result: MonitorResult) -> None:
        pass

    def on_monitors_passed(self, result: MonitorResult) -> None:
        pass

    def on_monitors_failed(self, result: MonitorResult) -> None:
        pass
