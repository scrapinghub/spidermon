from __future__ import absolute_import
from spidermon import Monitor, MonitorSuite, monitors


class DummyMonitor(Monitor):
    def runTest(self):
        pass


class DummyMonitorSuite(MonitorSuite):
    monitors = [DummyMonitor]


# ----------------------------------
# Monitors ordering
# ----------------------------------
class Unordered:
    class A(DummyMonitor):
        pass

    class B(DummyMonitor):
        pass

    class C(DummyMonitorSuite):
        pass

    class D(DummyMonitorSuite):
        pass


class Ordered:
    @monitors.order(1)
    class A(DummyMonitor):
        pass

    @monitors.order(2)
    class B(DummyMonitor):
        pass

    @monitors.order(3)
    class C(DummyMonitorSuite):
        pass

    @monitors.order(4)
    class D(DummyMonitorSuite):
        pass


# ----------------------------------
# Methods ordering
# ----------------------------------
class UnorderedMethodsMonitor(Monitor):
    def test_a(self):
        pass

    def test_b(self):
        pass

    def test_c(self):
        pass


class OrderedMethodsMonitor(Monitor):
    @monitors.order(3)
    def test_a(self):
        pass

    @monitors.order(2)
    def test_b(self):
        pass

    @monitors.order(1)
    def test_c(self):
        pass


class EqualOrderedMethodsMonitor(Monitor):
    @monitors.order(5)
    def test_a(self):
        pass

    @monitors.order(5)
    def test_b(self):
        pass

    @monitors.order(5)
    def test_c(self):
        pass
