import six

from unittest import TestSuite
import inspect
import collections

from spidermon.exceptions import (InvalidMonitorIterable, NotAllowedMethod)
from spidermon import settings

from .monitors import Monitor
from .options import MonitorOptionsMetaclass
from .factories import MonitorFactory, ActionFactory


class MonitorSuite(TestSuite):
    __metaclass__ = MonitorOptionsMetaclass

    monitors = []
    test_finish_actions = []
    test_pass_actions = []
    test_fail_actions = []

    def __init__(self, name=None, monitors=None,
                 test_finish_actions=None,
                 test_pass_actions=None,
                 test_fail_actions=None,
                 order=None):
        self._tests = []
        self._name = name
        self._parent = None
        self._order = order

        self.add_monitors(self.monitors)
        self.add_monitors(monitors or [])

        declarative_test_finish_actions = self.test_finish_actions
        self.test_finish_actions = []
        self.add_test_finish_actions(declarative_test_finish_actions)
        self.add_test_finish_actions(test_finish_actions or [])

        declarative_test_pass_actions = self.test_pass_actions
        self.test_pass_actions = []
        self.add_test_pass_actions(declarative_test_pass_actions)
        self.add_test_pass_actions(test_pass_actions or [])

        declarative_test_fail_actions = self.test_fail_actions
        self.test_fail_actions = []
        self.add_test_fail_actions(declarative_test_fail_actions)
        self.add_test_fail_actions(test_fail_actions or [])


    @property
    def name(self):
        return self._name or \
               self.options.name or \
               self.__class__.__name__

    @property
    def level(self):
        return self.options.level or \
               self.parent_level

    @property
    def parent_level(self):
        if self.parent:
            return self.parent.level
        return settings.DEFAULT_MONITOR_LEVEL

    @property
    def full_name(self):
        parts = []
        if self.parent and self.parent.full_name:
            parts.append(self.parent.full_name)
        if self.have_custom_name:
            parts.append(self.name)
        return '/'.join(parts)

    @property
    def have_custom_name(self):
        return self._name or \
               self.options.name

    @property
    def description(self):
        return self.options.description or \
               self.__class__.__doc__ or \
               settings.DEFAULT_DESCRIPTION

    @property
    def parent(self):
        return self._parent

    @property
    def order(self):
        return self._order if self._order is not None else None or \
               self.options.order

    @property
    def number_of_tests(self):
        return sum([1 if isinstance(test, Monitor) else test.number_of_tests
                    for test in self])

    @property
    def all_tests(self):
        tests = []
        for test in self:
            if isinstance(test, Monitor):
                tests += [test]
            else:
                tests += test.all_tests
        return tests

    def set_parent(self, parent):
        self._parent = parent

    def init_data(self, **data):
        for test in self:
            test.init_data(**data)

    def add_monitors(self, monitors):
        if not isinstance(monitors, collections.Iterable):
            raise InvalidMonitorIterable('Monitors definition is not iterable')
        for m in monitors:
            self.add_monitor(m)

    def add_monitor(self, monitor, name=None):
        monitor = MonitorFactory.load_monitor(monitor, name)
        monitor.set_parent(self)
        super(MonitorSuite, self).addTest(monitor)
        self._reorder_tests()

    def add_test_finish_actions(self, actions):
        for action in actions:
            self.add_test_finish_action(action)

    def add_test_finish_action(self, action):
        self._add_action(action, self.test_finish_actions)

    def add_test_pass_actions(self, actions):
        for action in actions:
            self.add_test_pass_action(action)

    def add_test_pass_action(self, action):
        self._add_action(action, self.test_pass_actions)

    def add_test_fail_actions(self, actions):
        for action in actions:
            self.add_test_fail_action(action)

    def add_test_fail_action(self, action):
        self._add_action(action, self.test_fail_actions)

    def _add_action(self, action, target_actions_list):
        action = ActionFactory.load_action(action)
        target_actions_list.append(action)

    def debug_tree(self, level=0):
        s = level*'\t' + repr(self) + '\n'
        for test in self:
            s += test.debug_tree(level=level+1)
        return s

    def debug_tests(self, show_monitor=True, show_method=True, show_level=True,
                    show_order=False, show_description=True):
        def debug_attribute(condition, name, value):
            return '%12s: %s\n' % (name, str(value)) if condition else ''
        s = '-'*80 + '\n'
        for t in self.all_tests:
            s += debug_attribute(show_monitor,      'MONITOR',      t.monitor_full_name)
            s += debug_attribute(show_method,       'METHOD',       t.method_name)
            s += debug_attribute(show_level,        'LEVEL',        t.level)
            s += debug_attribute(show_order,        'ORDER',        t.order)
            s += debug_attribute(show_description,  'DESCRIPTION',  t.method_description or '...')
            s += '-'*80 + '\n'
        return s

    def _reorder_tests(self):
        self._tests = sorted(self._tests, key=lambda x: x.order, reverse=False)

    def __repr__(self):
        return '<SUITE:%s[%d,%s] at %s>' % (self.name, len(self._tests), self.number_of_tests, hex(id(self)))

    def __str__(self):
        return self.name

    def __not_allowed_method(self, *args, **kwargs):
        raise NotAllowedMethod

    addTest = __not_allowed_method
    addTests = __not_allowed_method

    def on_tests_finished(self, result):
        pass

    def on_tests_passed(self, result):
        pass

    def on_tests_failed(self, result):
        pass
