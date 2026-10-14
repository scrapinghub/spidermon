from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, NoReturn

from spidermon.exceptions import (
    InvalidMonitor,
    InvalidMonitorClass,
    InvalidMonitorTuple,
)

from .actions import Action
from .monitors import Monitor

if TYPE_CHECKING:
    from scrapy.crawler import Crawler

    from .suites import MonitorSuite

# Length of a valid monitor tuple (name, monitor)
MONITOR_TUPLE_LENGTH = 2


class MonitorFactory:
    @classmethod
    def load_monitor(
        cls,
        monitor: object,
        name: str | None = None,
    ) -> Monitor | MonitorSuite:
        from .suites import MonitorSuite  # noqa: PLC0415

        if inspect.isclass(monitor):
            return cls.load_monitor_from_class(monitor_class=monitor, name=name)
        if isinstance(monitor, tuple):
            return cls.load_monitor_from_tuple(monitor_tuple=monitor)
        if isinstance(monitor, (Monitor, MonitorSuite)):
            return monitor
        cls.raise_invalid_monitor()
        return None

    @classmethod
    def load_monitor_from_class(
        cls,
        monitor_class: type,
        name: str | None = None,
    ) -> Monitor | MonitorSuite:
        from .suites import MonitorSuite  # noqa: PLC0415

        if issubclass(monitor_class, Monitor):
            from spidermon.loaders import MonitorLoader  # noqa: PLC0415

            loader = MonitorLoader()
            monitor = loader.load_suite_from_monitor(
                monitor_class=monitor_class,
                name=name,
            )
        elif issubclass(monitor_class, MonitorSuite):
            monitor = monitor_class(name=name)
        else:
            cls.raise_invalid_class()
        return cls.load_monitor(monitor=monitor, name=name)

    @classmethod
    def load_monitor_from_tuple(
        cls,
        monitor_tuple: tuple[Any, ...],
    ) -> Monitor | MonitorSuite:
        if len(monitor_tuple) != MONITOR_TUPLE_LENGTH:
            cls.raise_invalid_tuple()
        name, monitor = monitor_tuple
        if not isinstance(name, str):
            cls.raise_invalid_tuple()
        return cls.load_monitor(monitor=monitor, name=name)

    @classmethod
    def raise_invalid_monitor(cls) -> NoReturn:
        raise InvalidMonitor(
            "Wrong Monitor definition, it should be:\n"
            "- an instance of a Monitor/MonitorSuite object.\n"
            "- a subclass of Monitor/MonitorSuite.\n"
            "- a tuple with the format (name, monitor).\n"
            "- a string containing an evaluable python expression.",
        )

    @classmethod
    def raise_invalid_class(cls) -> NoReturn:
        raise InvalidMonitorClass(
            "Wrong Monitor class definition, it should be "
            "an instance of a Monitor/MonitorSuite object.",
        )

    @classmethod
    def raise_invalid_tuple(cls) -> NoReturn:
        raise InvalidMonitorTuple(
            "Wrong Monitor tuple definition, it should be "
            "a tuple with the format (name, monitor)",
        )


class ActionFactory:
    @classmethod
    def load_action(cls, action: object, crawler: Crawler | None = None) -> Action:
        if inspect.isclass(action):
            return cls.load_action_from_class(action_class=action, crawler=crawler)
        if isinstance(action, Action):
            return action
        cls.raise_invalid_action()
        return None

    @classmethod
    def load_action_from_class(
        cls,
        action_class: type,
        crawler: Crawler | None = None,
    ) -> Action:
        if not issubclass(action_class, Action):
            cls.raise_invalid_class()
        if crawler and hasattr(action_class, "from_crawler"):
            return action_class.from_crawler(crawler)
        return action_class()

    @classmethod
    def raise_invalid_action(cls) -> NoReturn:
        raise InvalidMonitor(
            "Wrong Monitor definition, it should be:\n"
            "- an instance of a Monitor/MonitorSuite object.\n"
            "- a subclass of Monitor/MonitorSuite.\n"
            "- a tuple with the format (name, monitor).\n"
            "- a string containing an evaluable python expression.",
        )

    @classmethod
    def raise_invalid_class(cls) -> NoReturn:
        raise InvalidMonitorClass(
            "Wrong Monitor class definition, it should be "
            "an instance of a Monitor/MonitorSuite object.",
        )
