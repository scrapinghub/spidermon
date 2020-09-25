from __future__ import absolute_import
import six

from unittest import TestSuite
import inspect
import collections

from spidermon.exceptions import InvalidMonitorIterable, NotAllowedMethod
from spidermon import settings

from .monitors import Monitor
from .options import MonitorOptionsMetaclass
from .factories import MonitorFactory, ActionFactory


class MonitorSuite(six.with_metaclass(MonitorOptionsMetaclass, TestSuite)):
    monitors = []
    monitors_finished_actions = []
    monitors_passed_actions = []
    monitors_failed_actions = []

    def __init__(
        self,
        name=None,
        monitors=None,
        monitors_finished_actions=None,
        monitors_passed_actions=None,
        monitors_failed_actions=None,
        order=None,
        crawler=None,
    ):
        self._tests = []
        self._removed_tests = 0
        self._name = name
        self._parent = None
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
    def name(self):
        return self._name or self.options.name or self.__class__.__name__

    @property
    def level(self):
        return self.options.level or self.parent_level

    @property
    def parent_level(self):
        if self.parent:
            return self.parent.level
        return settings.MONITOR.LEVELS.DEFAULT

    @property
    def full_name(self):
        parts = []
        if self.parent and self.parent.full_name:
            parts.append(self.parent.full_name)
        if self.have_custom_name:
            parts.append(self.name)
        return "/".join(parts)

    @property
    def have_custom_name(self):
        return self._name or self.options.name

    @property
    def description(self):
        return (
            self.options.description
            or self.__class__.__doc__
            or settings.MONITOR.DEFAULT_DESCRIPTION
        )

    @property
    def parent(self):
        return self._parent

    @property
    def order(self):
        return self._order if self._order is not None else None or self.options.order

    @property
    def number_of_monitors(self):
        return sum(
            [
                1 if isinstance(monitor, Monitor) else monitor.number_of_monitors
                for monitor in self
            ]
        )

    @property
    def all_monitors(self):
        monitors = []
        for monitor in self:
            if isinstance(monitor, Monitor):
                monitors += [monitor]
            else:
                monitors += monitor.all_monitors
        return monitors

    def set_parent(self, parent):
        self._parent = parent

    def init_data(self, data):
        for test in self:
            test.init_data(data)

    def add_monitors(self, monitors):
        if not isinstance(monitors, collections.abc.Iterable):
            raise InvalidMonitorIterable("Monitors definition is not iterable")
        for m in monitors:
            self.add_monitor(m)

    def add_monitor(self, monitor, name=None):
        monitor = MonitorFactory.load_monitor(monitor, name)
        monitor.set_parent(self)
        super(MonitorSuite, self).addTest(monitor)
        self._reorder_tests()

    def add_monitors_finished_actions(self, actions):
        for action in actions:
            self.add_monitors_finished_action(action)

    def add_monitors_finished_action(self, action):
        self._add_action(action, self.monitors_finished_actions)

    def add_monitors_passed_actions(self, actions):
        for action in actions:
            self.add_monitors_passed_action(action)

    def add_monitors_passed_action(self, action):
        self._add_action(action, self.monitors_passed_actions)

    def add_monitors_failed_actions(self, actions):
        for action in actions:
            self.add_monitors_failed_action(action)

    def add_monitors_failed_action(self, action):
        self._add_action(action, self.monitors_failed_actions)

    def _add_action(self, action, target_actions_list):
        action = ActionFactory.load_action(action, crawler=self._crawler)
        target_actions_list.append(action)

    def debug_tree(self, level=0):
        s = level * "\t" + repr(self) + "\n"
        for test in self:
            s += test.debug_tree(level=level + 1)
        return s

    def debug_monitors(
        self,
        show_monitor=True,
        show_method=True,
        show_level=True,
        show_order=False,
        show_description=True,
    ):
        def debug_attribute(condition, name, value):
            return "%12s: %s\n" % (name, str(value)) if condition else ""

        s = "-" * 80 + "\n"
        for t in self.all_monitors:
            s += debug_attribute(show_monitor, "MONITOR", t.monitor_full_name)
            s += debug_attribute(show_method, "METHOD", t.method_name)
            s += debug_attribute(show_level, "LEVEL", t.level)
            s += debug_attribute(show_order, "ORDER", t.order)
            s += debug_attribute(
                show_description, "DESCRIPTION", t.method_description or "..."
            )
            s += "-" * 80 + "\n"
        return s

    def _reorder_tests(self):
        self._tests = sorted(self._tests, key=lambda x: x.order, reverse=False)

    def __repr__(self):
        return "<SUITE:%s[%d,%s] at %s>" % (
            self.name,
            len(self._tests),
            self.number_of_monitors,
            hex(id(self)),
        )

    def __str__(self):
        return self.name

    def __not_allowed_method(self, *args, **kwargs):
        raise NotAllowedMethod

    addTest = __not_allowed_method
    addTests = __not_allowed_method

    def on_monitors_finished(self, result):
        pass

    def on_monitors_passed(self, result):
        pass

    def on_monitors_failed(self, result):
        pass
