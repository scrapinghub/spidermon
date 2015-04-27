import unittest
from objects import StatsMonitorObject, JobMonitorObject

__all__ = ['StatsMonitor', 'JobMonitor']


class MonitorBase(unittest.TestCase):

    def __init__(self, methodName='runTest', name=None):
        super(MonitorBase, self).__init__(methodName)
        self._name = name

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return '<MONITOR:%s at %s>' % (str(self), hex(id(self)))

    def __str__(self):
        return '%s.%s' % (self.__class__.__name__, self._testMethodName)
        #return self.name or '%s.%s' % (self.__class__.__name__, self._testMethodName)

    def debug(self, level=0):
        print level*'\t' + repr(self)

    @property
    def number_of_tests(self):
        return 1

    @property
    def all_tests(self):
        return [self]


class StatsMonitor(MonitorBase, StatsMonitorObject):
    pass


class JobMonitor(MonitorBase, JobMonitorObject):
    pass
