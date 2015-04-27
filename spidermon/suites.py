import unittest
import inspect
import collections

from objects import StatsMonitorObject, JobMonitorObject
from monitors import MonitorBase


class MonitorSuite(unittest.TestSuite):

    monitors = []

    def __init__(self, monitors=(), name=None):
        self._tests = []
        self.add_monitors(self.monitors)
        self.add_monitors(monitors)
        self._name = name

    @property
    def name(self):
        return self._name or self.__doc__ or self.__class__.__name__

    def init_child_data(self, **data):
        for test in self:
            test.set_data(**data)

    def __repr__(self):
        return '<SUITE:%s[%d,%s] at %s>' % (self.name, len(self._tests), self.number_of_tests, hex(id(self)))

    def __str__(self):
        return self.__repr__()

    def add_monitors(self, monitors):
        if not isinstance(monitors, collections.Iterable):
            raise Exception('Not iterable')  # TODO: Custom exception
        for m in monitors:
            self.add_monitor(m)

    def add_monitor(self, monitor, name=None):
        if inspect.isclass(monitor):
            return self._add_monitor_from_class(monitor_class=monitor, name=name)
        elif isinstance(monitor, tuple):
            return self._add_monitor_from_tuple(monitor_tuple=monitor)
        elif isinstance(monitor, (MonitorBase, MonitorSuite)):
            return super(MonitorSuite, self).addTest(monitor)
        raise Exception('Not valid monitor')  # TODO: Custom exception

    def _add_monitor_from_class(self, monitor_class, name=None):
        if issubclass(monitor_class, MonitorBase):
            from loaders import MonitorLoader
            loader = MonitorLoader()
            monitor = loader.load_suite_from_monitor(monitor_class)
        elif issubclass(monitor_class, MonitorSuite):
            monitor = monitor_class(name=name)
        else:
            raise Exception('Not valid monitor')  # TODO: Custom exception
        return self.add_monitor(monitor=monitor, name=name)

    def _add_monitor_from_tuple(self, monitor_tuple):
        if len(monitor_tuple) != 2:
            raise Exception('Not valid monitor')  # TODO: Custom exception
        monitor, name = monitor_tuple
        return self.add_monitor(monitor=monitor, name=name)

    def __not_allowed_method(self, *args, **kwargs):
        raise Exception  # TODO: Custom exception

    addTest = __not_allowed_method
    addTests = __not_allowed_method

    def debug(self, level=0):
        print level*'\t' + repr(self)
        for test in self:
            test.debug(level=level+1)

    @property
    def number_of_tests(self):
        return sum([t.number_of_tests for t in self])

    @property
    def all_tests(self):
        tests = []
        for test in self:
            tests += test.all_tests
        return tests


class StatsMonitorSuite(MonitorSuite, StatsMonitorObject):
    pass


class JobMonitorSuite(MonitorSuite, JobMonitorObject):
    pass
