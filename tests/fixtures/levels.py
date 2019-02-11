from __future__ import absolute_import
from spidermon import Monitor, MonitorSuite, monitors


# ----------------------------------
# Base Monitors
# ----------------------------------
class NoLevelMethodMonitor(Monitor):
    def test(self):
        pass


class HighLevelMethodMonitor(Monitor):
    @monitors.level.high
    def test(self):
        pass


class NormalLevelMethodMonitor(Monitor):
    @monitors.level.normal
    def test(self):
        pass


class LowLevelMethodMonitor(Monitor):
    @monitors.level.low
    def test(self):
        pass


# ----------------------------------
# Monitors
# ----------------------------------
class Monitors:
    class NoLevelMonitor:
        class NoLevelMethod(NoLevelMethodMonitor):
            pass

        class HighLevelMethod(HighLevelMethodMonitor):
            pass

        class NormalLevelMethod(NormalLevelMethodMonitor):
            pass

        class LowLevelMethod(LowLevelMethodMonitor):
            pass

    class HighLevelMonitor:
        @monitors.level.high
        class NoLevelMethod(NoLevelMethodMonitor):
            pass

        @monitors.level.high
        class HighLevelMethod(HighLevelMethodMonitor):
            pass

        @monitors.level.high
        class NormalLevelMethod(NormalLevelMethodMonitor):
            pass

        @monitors.level.high
        class LowLevelMethod(LowLevelMethodMonitor):
            pass

    class NormalLevelMonitor:
        @monitors.level.normal
        class NoLevelMethod(NoLevelMethodMonitor):
            pass

        @monitors.level.normal
        class HighLevelMethod(HighLevelMethodMonitor):
            pass

        @monitors.level.normal
        class NormalLevelMethod(NormalLevelMethodMonitor):
            pass

        @monitors.level.normal
        class LowLevelMethod(LowLevelMethodMonitor):
            pass

    class LowLevelMonitor:
        @monitors.level.low
        class NoLevelMethod(NoLevelMethodMonitor):
            pass

        @monitors.level.low
        class HighLevelMethod(HighLevelMethodMonitor):
            pass

        @monitors.level.low
        class NormalLevelMethod(NormalLevelMethodMonitor):
            pass

        @monitors.level.low
        class LowLevelMethod(LowLevelMethodMonitor):
            pass


# ----------------------------------
# Suites
# ----------------------------------
class Suites:
    class NoLevelSuite(MonitorSuite):
        pass

    @monitors.level.high
    class HighLevelSuite(MonitorSuite):
        pass

    @monitors.level.normal
    class NormalLevelSuite(MonitorSuite):
        pass

    @monitors.level.low
    class LowLevelSuite(MonitorSuite):
        pass
