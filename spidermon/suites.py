import six

from unittest import TestSuite
import inspect
import collections

from .monitors import Monitor
from .options import OptionsMetaclass
from .exceptions import (InvalidMonitor,
                         InvalidMonitorIterable, InvalidMonitorClass, InvalidMonitorTuple,
                         NotAllowedMethod)


class MonitorSuite(TestSuite):
    __metaclass__ = OptionsMetaclass

    monitors = []

    def __init__(self, monitors=(), name=None):
        self._tests = []
        self.add_monitors(self.monitors)
        self.add_monitors(monitors)
        self._name = name
        self._parent = None

    @property
    def name(self):
        return self._name or \
               self.options.name or \
               self.__class__.__name__

    @property
    def full_name(self):
        parts = []
        if self.parent and self.parent.full_name:
            parts.append(self.parent.full_name)
        if self.custom_name:
            parts.append(self.name)
        return '/'.join(parts)

    @property
    def custom_name(self):
        return self._name or \
               self.options.name

    @property
    def parent(self):
        return self._parent

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
        if inspect.isclass(monitor):
            return self._add_monitor_from_class(monitor_class=monitor, name=name)
        elif isinstance(monitor, tuple):
            return self._add_monitor_from_tuple(monitor_tuple=monitor)
        elif isinstance(monitor, (Monitor, MonitorSuite)):
            monitor.set_parent(self)
            return super(MonitorSuite, self).addTest(monitor)
        self._raise_invalid()

    def debug(self, level=0):
        print level*'\t' + repr(self)
        for test in self:
            test.debug(level=level+1)

    def _add_monitor_from_class(self, monitor_class, name=None):
        if issubclass(monitor_class, Monitor):
            from loaders import MonitorLoader
            loader = MonitorLoader()
            monitor = loader.load_suite_from_monitor(monitor_class=monitor_class, name=name)
        elif issubclass(monitor_class, MonitorSuite):
            monitor = monitor_class(name=name)
        else:
            self._raise_invalid_class()
        return self.add_monitor(monitor=monitor, name=name)

    def _add_monitor_from_tuple(self, monitor_tuple):
        if len(monitor_tuple) != 2:
            self._raise_invalid_tuple()
        name, monitor = monitor_tuple
        if not isinstance(name, six.string_types):
            self._raise_invalid_tuple()
        return self.add_monitor(monitor=monitor, name=name)

    def _raise_invalid(self):
        raise InvalidMonitor('Wrong Monitor definition, it should be:\n'
                             '- an instance of a Monitor/MonitorSuite object.\n'
                             '- a subclass of Monitor/MonitorSuite.\n'
                             '- a tuple with the format (name, monitor).\n'
                             '- a string containing an evaluable python expression.')

    def _raise_invalid_class(self):
        raise InvalidMonitorClass('Wrong Monitor class definition, it should be '
                                  'an instance of a Monitor/MonitorSuite object.')

    def _raise_invalid_tuple(self):
        raise InvalidMonitorTuple('Wrong Monitor tuple definition, it should be '
                                  'a tuple with the format (name, monitor)')

    def __not_allowed_method(self, *args, **kwargs):
        raise NotAllowedMethod

    def __repr__(self):
        return '<SUITE:%s[%d,%s] at %s>' % (self.name, len(self._tests), self.number_of_tests, hex(id(self)))

    def __str__(self):
        return self.name

    addTest = __not_allowed_method
    addTests = __not_allowed_method
