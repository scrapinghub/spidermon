from __future__ import absolute_import
from spidermon import settings

from .fixtures.levels import *

HIGH = settings.MONITOR.LEVEL.HIGH
NORMAL = settings.MONITOR.LEVEL.NORMAL
LOW = settings.MONITOR.LEVEL.LOW


LEVEL_TESTS = [
    # ---------------------------------------------------------------------------------------
    # suite                     monitor/methods                                expected level
    # ---------------------------------------------------------------------------------------
    # Suite No Level
    (Suites.NoLevelSuite, Monitors.NoLevelMonitor.NoLevelMethod, NORMAL),
    (Suites.NoLevelSuite, Monitors.NoLevelMonitor.HighLevelMethod, HIGH),
    (Suites.NoLevelSuite, Monitors.NoLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.NoLevelSuite, Monitors.NoLevelMonitor.LowLevelMethod, LOW),
    (Suites.NoLevelSuite, Monitors.HighLevelMonitor.NoLevelMethod, HIGH),
    (Suites.NoLevelSuite, Monitors.HighLevelMonitor.HighLevelMethod, HIGH),
    (Suites.NoLevelSuite, Monitors.HighLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.NoLevelSuite, Monitors.HighLevelMonitor.LowLevelMethod, LOW),
    (Suites.NoLevelSuite, Monitors.NormalLevelMonitor.NoLevelMethod, NORMAL),
    (Suites.NoLevelSuite, Monitors.NormalLevelMonitor.HighLevelMethod, HIGH),
    (Suites.NoLevelSuite, Monitors.NormalLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.NoLevelSuite, Monitors.NormalLevelMonitor.LowLevelMethod, LOW),
    (Suites.NoLevelSuite, Monitors.LowLevelMonitor.NoLevelMethod, LOW),
    (Suites.NoLevelSuite, Monitors.LowLevelMonitor.HighLevelMethod, HIGH),
    (Suites.NoLevelSuite, Monitors.LowLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.NoLevelSuite, Monitors.LowLevelMonitor.LowLevelMethod, LOW),
    # Suite High
    (Suites.HighLevelSuite, Monitors.NoLevelMonitor.NoLevelMethod, HIGH),
    (Suites.HighLevelSuite, Monitors.NoLevelMonitor.HighLevelMethod, HIGH),
    (Suites.HighLevelSuite, Monitors.NoLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.HighLevelSuite, Monitors.NoLevelMonitor.LowLevelMethod, LOW),
    (Suites.HighLevelSuite, Monitors.HighLevelMonitor.NoLevelMethod, HIGH),
    (Suites.HighLevelSuite, Monitors.HighLevelMonitor.HighLevelMethod, HIGH),
    (Suites.HighLevelSuite, Monitors.HighLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.HighLevelSuite, Monitors.HighLevelMonitor.LowLevelMethod, LOW),
    (Suites.HighLevelSuite, Monitors.NormalLevelMonitor.NoLevelMethod, NORMAL),
    (Suites.HighLevelSuite, Monitors.NormalLevelMonitor.HighLevelMethod, HIGH),
    (Suites.HighLevelSuite, Monitors.NormalLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.HighLevelSuite, Monitors.NormalLevelMonitor.LowLevelMethod, LOW),
    (Suites.HighLevelSuite, Monitors.LowLevelMonitor.NoLevelMethod, LOW),
    (Suites.HighLevelSuite, Monitors.LowLevelMonitor.HighLevelMethod, HIGH),
    (Suites.HighLevelSuite, Monitors.LowLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.HighLevelSuite, Monitors.LowLevelMonitor.LowLevelMethod, LOW),
    # Suite Normal
    (Suites.NormalLevelSuite, Monitors.NoLevelMonitor.NoLevelMethod, NORMAL),
    (Suites.NormalLevelSuite, Monitors.NoLevelMonitor.HighLevelMethod, HIGH),
    (Suites.NormalLevelSuite, Monitors.NoLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.NormalLevelSuite, Monitors.NoLevelMonitor.LowLevelMethod, LOW),
    (Suites.NormalLevelSuite, Monitors.HighLevelMonitor.NoLevelMethod, HIGH),
    (Suites.NormalLevelSuite, Monitors.HighLevelMonitor.HighLevelMethod, HIGH),
    (Suites.NormalLevelSuite, Monitors.HighLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.NormalLevelSuite, Monitors.HighLevelMonitor.LowLevelMethod, LOW),
    (Suites.NormalLevelSuite, Monitors.NormalLevelMonitor.NoLevelMethod, NORMAL),
    (Suites.NormalLevelSuite, Monitors.NormalLevelMonitor.HighLevelMethod, HIGH),
    (Suites.NormalLevelSuite, Monitors.NormalLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.NormalLevelSuite, Monitors.NormalLevelMonitor.LowLevelMethod, LOW),
    (Suites.NormalLevelSuite, Monitors.LowLevelMonitor.NoLevelMethod, LOW),
    (Suites.NormalLevelSuite, Monitors.LowLevelMonitor.HighLevelMethod, HIGH),
    (Suites.NormalLevelSuite, Monitors.LowLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.NormalLevelSuite, Monitors.LowLevelMonitor.LowLevelMethod, LOW),
    # Suite Low
    (Suites.LowLevelSuite, Monitors.NoLevelMonitor.NoLevelMethod, LOW),
    (Suites.LowLevelSuite, Monitors.NoLevelMonitor.HighLevelMethod, HIGH),
    (Suites.LowLevelSuite, Monitors.NoLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.LowLevelSuite, Monitors.NoLevelMonitor.LowLevelMethod, LOW),
    (Suites.LowLevelSuite, Monitors.HighLevelMonitor.NoLevelMethod, HIGH),
    (Suites.LowLevelSuite, Monitors.HighLevelMonitor.HighLevelMethod, HIGH),
    (Suites.LowLevelSuite, Monitors.HighLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.LowLevelSuite, Monitors.HighLevelMonitor.LowLevelMethod, LOW),
    (Suites.LowLevelSuite, Monitors.NormalLevelMonitor.NoLevelMethod, NORMAL),
    (Suites.LowLevelSuite, Monitors.NormalLevelMonitor.HighLevelMethod, HIGH),
    (Suites.LowLevelSuite, Monitors.NormalLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.LowLevelSuite, Monitors.NormalLevelMonitor.LowLevelMethod, LOW),
    (Suites.LowLevelSuite, Monitors.LowLevelMonitor.NoLevelMethod, LOW),
    (Suites.LowLevelSuite, Monitors.LowLevelMonitor.HighLevelMethod, HIGH),
    (Suites.LowLevelSuite, Monitors.LowLevelMonitor.NormalLevelMethod, NORMAL),
    (Suites.LowLevelSuite, Monitors.LowLevelMonitor.LowLevelMethod, LOW),
]


def test_levels():
    for suite, monitor, expected_level in LEVEL_TESTS:
        suite = suite()
        suite.add_monitor(monitor)
        assert suite.all_monitors[0].level == expected_level
