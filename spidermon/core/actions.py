from __future__ import annotations

import abc
import traceback
from typing import TYPE_CHECKING, Any, ClassVar

from spidermon.exceptions import SkipAction

from .options import ActionOptions, ActionOptionsMetaclass

if TYPE_CHECKING:
    from scrapy.crawler import Crawler
    from typing_extensions import Self

    from spidermon.data import Data
    from spidermon.results.monitor import MonitorResult


class Action(metaclass=ActionOptionsMetaclass):
    """Base class for actions."""

    options: ClassVar[ActionOptions]
    fallback: Any = None
    """Action class to also run when :meth:`run_action` raises an exception."""

    def __init__(self) -> None:
        self.result: MonitorResult | None = None
        self.data: Data | None = None
        """Job data, the same as :attr:`Monitor.data
        <spidermon.core.monitors.Monitor.data>`."""
        if self.fallback is not None:
            self.fallback = self.fallback()

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        return cls(**cls.from_crawler_kwargs(crawler))

    @classmethod
    def from_crawler_kwargs(cls, crawler: Crawler) -> dict[str, Any]:
        return {}

    @property
    def name(self) -> str:
        return self.options.name or self.__class__.__name__

    def run(self, result: MonitorResult, data: Data) -> None:
        self.result = result
        self.data = data
        result.start_action(self)
        try:
            self.run_action()
        except SkipAction as e:
            result.add_action_skip(self, e.args[0])
        except:  # noqa: E722
            result.add_action_error(self, traceback.format_exc())
            if self.fallback is not None:
                self.fallback.run(self.result, self.data)
        else:
            result.add_action_success(self)
        data.meta.update(self.get_meta())

    @abc.abstractmethod
    def run_action(self) -> None:
        """Run the action. Subclasses must implement it."""
        raise NotImplementedError

    @property
    def monitors_passed(self) -> bool:
        """Whether any monitor passed."""
        assert self.result is not None
        return len(self.result.monitors_passed_results) > 0

    @property
    def monitors_failed(self) -> bool:
        """Whether any monitor failed."""
        assert self.result is not None
        return len(self.result.monitors_failed_results) > 0

    def get_meta(self) -> dict[str, Any]:
        return {}

    def __repr__(self) -> str:
        return f"<ACTION:({self.name}) at {hex(id(self))}>"

    def __str__(self) -> str:
        return repr(self)


class DummyAction(Action):
    def run_action(self) -> None:
        pass
