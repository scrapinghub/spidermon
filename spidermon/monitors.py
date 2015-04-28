from unittest import TestCase

from .stats import Stats


class MonitorBase(TestCase):
    def __init__(self, methodName='runTest', name=None):
        super(MonitorBase, self).__init__(methodName)
        self._name = name
        self._data = None

    def init_data(self, **data):
        self._data = data

    @property
    def name(self):
        return self._name or str(self)

    def __repr__(self):
        return '<MONITOR:%s at %s>' % (str(self), hex(id(self)))

    def __str__(self):
        return '%s.%s' % (self.__class__.__name__, self._testMethodName)

    def debug(self, level=0):
        print level*'\t' + repr(self)


class StatsMonitor(MonitorBase):
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
