from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, ClassVar
from unittest import TestCase

from spidermon import settings

from .options import MonitorOptions, MonitorOptionsMetaclass

if TYPE_CHECKING:
    from spidermon.data import Data

    from .suites import MonitorSuite


class Monitor(TestCase, metaclass=MonitorOptionsMetaclass):
    """Base class for monitors, holding the monitoring logic as test methods,
    the way a ``unittest.TestCase`` holds test methods.

    Test methods check :attr:`data` with the ``unittest.TestCase`` assertion
    methods, and a failed assertion is a failed monitor.

    The ``monitors`` decorators (``from spidermon import monitors``) set the
    metadata of a monitor class or of one of its test methods:
    ``@monitors.name("...")`` sets :attr:`monitor_name` or :attr:`method_name`,
    ``@monitors.description("...")`` sets :attr:`monitor_description` or
    :attr:`method_description`, and ``@monitors.order(n)`` sets the position
    among sibling monitors or test methods, lowest first and 1 by default.

    *name* overrides :attr:`monitor_name`. Monitor suites set it for monitors
    listed as ``(name, monitor_class)`` tuples.
    """

    options: ClassVar[MonitorOptions]

    data: Any = None
    """Job data, a :class:`~spidermon.data.Data`.

    The Scrapy extension fills it with ``stats``, the spider stats; ``crawler``
    and ``spider``, the Scrapy objects; and ``job``, the Scrapy Cloud job, or
    ``None`` when not running there.
    """

    def __init__(self, methodName: str = "runTest", name: str | None = None) -> None:
        super().__init__(methodName)
        self._name = name
        self._data = None
        self._parent: MonitorSuite | None = None
        self._init_method()

    @property
    def name(self) -> str:
        """:attr:`monitor_name` and :attr:`method_name`, slash-separated."""
        return f"{self.monitor_name}/{self.method_name}"

    @property
    def full_name(self) -> str:
        """:attr:`name` prefixed with the custom names of the enclosing suites,
        slash-separated."""
        parts = []
        if self.parent and self.parent.full_name:
            parts.append(self.parent.full_name)
        parts.append(self.name)
        return "/".join(parts)

    @property
    def level(self) -> int:
        return (
            self.method_level
            or self.monitor_level
            or self.parent_level
            or settings.MONITOR.LEVELS.DEFAULT
        )

    @property
    def order(self) -> int:
        options: MonitorOptions = self.method.options
        return options.order

    @property
    def monitor_name(self) -> str:
        """*name* from the constructor, else the class ``@monitors.name``, else
        the class name."""
        return self._name or self.options.name or self.__class__.__name__

    @property
    def monitor_full_name(self) -> str:
        parts = []
        if self.parent and self.parent.full_name:
            parts.append(self.parent.full_name)
        parts.append(self.monitor_name)
        return "/".join(parts)

    @property
    def monitor_description(self) -> str:
        """The class ``@monitors.description``, else the class docstring, else
        an empty string."""
        return (
            self.options.description
            or self.__class__.__doc__
            or settings.MONITOR.DEFAULT_DESCRIPTION
        )

    @property
    def monitor_level(self) -> int | None:
        return self.options.level

    @property
    def method(self) -> Any:
        return getattr(self, self._testMethodName)

    @property
    def method_name(self) -> str:
        """The test method ``@monitors.name``, else the method name."""
        return self.method.options.name or self._testMethodName

    @property
    def method_description(self) -> str:
        """The test method ``@monitors.description``, else its docstring, else
        an empty string."""
        return (
            self.method.options.description
            or self.method.__func__.__doc__
            or settings.MONITOR.DEFAULT_DESCRIPTION
        )

    @property
    def method_level(self) -> int | None:
        options: MonitorOptions = self.method.options
        return options.level

    @property
    def parent(self) -> MonitorSuite | None:
        return self._parent

    @property
    def parent_level(self) -> int:
        assert self.parent is not None
        return self.parent.level

    def set_parent(self, parent: MonitorSuite) -> None:
        self._parent = parent

    def init_data(self, data: Data) -> None:
        self.data = data

    def debug_tree(self, level: int = 0) -> str:
        return level * "\t" + repr(self) + "\n"

    def _init_method(self) -> None:
        if hasattr(self, self._testMethodName):
            MonitorOptions.add_or_create(self.method.__func__)

    def utc_now_with_timezone(self) -> datetime:
        return datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<MONITOR:({self.name}) at {hex(id(self))}>"

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(id(self))
