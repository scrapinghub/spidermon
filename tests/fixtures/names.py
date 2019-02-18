from __future__ import absolute_import
from spidermon import monitors, Monitor, MonitorSuite


# ----------------------------------
# Monitors
# ----------------------------------
class UnnamedMonitor(Monitor):
    def test_without_name(self):
        pass

    @monitors.name("A Test")
    def test_with_name(self):
        pass


@monitors.name("Class Monitor")
class NamedMonitor(Monitor):
    def test_without_name(self):
        pass

    @monitors.name("A Test")
    def test_with_name(self):
        pass


# ----------------------------------
# Child Suites
# ----------------------------------
class BaseChildSuite(MonitorSuite):
    monitors = [
        UnnamedMonitor,
        NamedMonitor,
        ("Instance Monitor", UnnamedMonitor),
        ("Instance Monitor", NamedMonitor),
    ]


class ChildUnnamedSuite(BaseChildSuite):
    pass


@monitors.name("The Child Suite")
class ChildNamedSuite(BaseChildSuite):
    pass


# ----------------------------------
# Top Suites
# ----------------------------------
class BaseTopSuite(MonitorSuite):
    monitors = [
        ChildUnnamedSuite,
        ChildNamedSuite,
        ("Instance Suite Name", ChildUnnamedSuite),
        ("Instance Suite Name", ChildNamedSuite),
    ]


class UnnamedTopSuite(BaseTopSuite):
    pass


@monitors.name("The Top Suite")
class NamedTopSuite(BaseTopSuite):
    pass
