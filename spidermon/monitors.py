from unittest import TestCase

from .stats import Stats


class Monitor(TestCase):
    def __init__(self, methodName='runTest', name=None):
        super(Monitor, self).__init__(methodName)
        self._name = name
        self._data = None
        self._parent = None

    def set_parent(self, parent):
        self._parent = parent

    def init_data(self, **data):
        self._data = data

    @property
    def name(self):
        return self._name or str(self)

    @property
    def monitor_name(self):
        return self.__doc__

    @property
    def test_name(self):
        return self._name or self._testMethodName

    @property
    def full_name(self):
        parts = []
        if self.parent and self.parent.full_name:
            parts.append(self.parent.full_name)
        if self.monitor_name:
            parts.append(self.monitor_name)
        if not parts:
            return self.name
        else:
            parts.append(self.test_name)
            return '/'.join(parts)

    @property
    def parent(self):
        return self._parent

    def __repr__(self):
        return '<MONITOR:%s at %s>' % (str(self), hex(id(self)))

    def __str__(self):
        return '%s.%s' % (self.__class__.__name__, self._testMethodName)

    def debug(self, level=0):
        print level*'\t' + repr(self)


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
