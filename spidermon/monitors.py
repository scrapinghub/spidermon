from unittest import TestCase

from .stats import Stats
from .options import OptionsMetaclass, Options


class Monitor(TestCase):
    __metaclass__ = OptionsMetaclass

    def __init__(self, methodName='runTest', name=None):
        super(Monitor, self).__init__(methodName)
        self._name = name
        self._data = None
        self._parent = None
        self._init_test_method()

    @property
    def monitor_name(self):
        return self._name or \
               self.options.name or \
               self.__class__.__name__

    @property
    def test_method_name(self):
        return self.test_method.options.name or \
               self._testMethodName

    @property
    def name(self):
        return ':'.join([self.monitor_name, self.test_method_name])

    @property
    def test_method(self):
        return getattr(self, self._testMethodName)

    @property
    def full_name(self):
        parts = []
        if self.parent and self.parent.full_name:
            parts.append(self.parent.full_name)
        parts.append(self.name)
        return '/'.join(parts)

    @property
    def parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent

    def init_data(self, **data):
        self._data = data

    def debug(self, level=0):
        print level*'\t' + repr(self)

    def _init_test_method(self):
        Options.add_or_create(self.test_method.__func__)

    def __repr__(self):
        return '<MONITOR:(%s) at %s>' % (self.name, hex(id(self)))

    def __str__(self):
        return self.name


class StatsMonitor(Monitor):
    def __init__(self, methodName='runTest', name=None):
        super(StatsMonitor, self).__init__(methodName, name)
        self.stats = Stats()

    def init_data(self, **data):
        super(StatsMonitor, self).init_data(**data)
        stats = data.get('stats')
        if stats:
            self.stats = Stats(stats)


class JobMonitor(StatsMonitor):
    def __init__(self, methodName='runTest', name=None):
        super(JobMonitor, self).__init__(methodName, name)
        self.job = {}

    def init_data(self, **data):
        super(StatsMonitor, self).init_data(**data)
        self.job = data.get('job')
