from datetime import datetime, timezone
from unittest import TestCase

from spidermon import settings

from .options import MonitorOptions, MonitorOptionsMetaclass


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

    data = None
    """Job data, a dict whose keys are also attributes.

    The Scrapy extension fills it with ``stats``, the spider stats; ``crawler``
    and ``spider``, the Scrapy objects; and ``job``, the Scrapy Cloud job, or
    ``None`` when not running there.
    """

    def __init__(self, methodName="runTest", name=None):
        super().__init__(methodName)
        self._name = name
        self._data = None
        self._parent = None
        self._init_method()

    @property
    def name(self):
        """:attr:`monitor_name` and :attr:`method_name`, slash-separated."""
        return f"{self.monitor_name}/{self.method_name}"

    @property
    def full_name(self):
        """:attr:`name` prefixed with the custom names of the enclosing suites,
        slash-separated."""
        parts = []
        if self.parent and self.parent.full_name:
            parts.append(self.parent.full_name)
        parts.append(self.name)
        return "/".join(parts)

    @property
    def level(self):
        return (
            self.method_level
            or self.monitor_level
            or self.parent_level
            or settings.MONITOR.LEVELS.DEFAULT
        )

    @property
    def order(self):
        return self.method.options.order

    @property
    def monitor_name(self):
        """*name* from the constructor, else the class ``@monitors.name``, else
        the class name."""
        return self._name or self.options.name or self.__class__.__name__

    @property
    def monitor_full_name(self):
        parts = []
        if self.parent and self.parent.full_name:
            parts.append(self.parent.full_name)
        parts.append(self.monitor_name)
        return "/".join(parts)

    @property
    def monitor_description(self):
        """The class ``@monitors.description``, else the class docstring, else
        an empty string."""
        return (
            self.options.description
            or self.__class__.__doc__
            or settings.MONITOR.DEFAULT_DESCRIPTION
        )

    @property
    def monitor_level(self):
        return self.options.level

    @property
    def method(self):
        return getattr(self, self._testMethodName)

    @property
    def method_name(self):
        """The test method ``@monitors.name``, else the method name."""
        return self.method.options.name or self._testMethodName

    @property
    def method_description(self):
        """The test method ``@monitors.description``, else its docstring, else
        an empty string."""
        return (
            self.method.options.description
            or self.method.__func__.__doc__
            or settings.MONITOR.DEFAULT_DESCRIPTION
        )

    @property
    def method_level(self):
        return self.method.options.level

    @property
    def parent(self):
        return self._parent

    @property
    def parent_level(self):
        return self.parent.level

    def set_parent(self, parent):
        self._parent = parent

    def init_data(self, data):
        self.data = data

    def debug_tree(self, level=0):
        return level * "\t" + repr(self) + "\n"

    def _init_method(self):
        if hasattr(self, self._testMethodName):
            MonitorOptions.add_or_create(self.method.__func__)

    def utc_now_with_timezone(self):
        return datetime.now(timezone.utc)

    def __repr__(self):
        return f"<MONITOR:({self.name}) at {hex(id(self))}>"

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(id(self))
