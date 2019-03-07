from __future__ import absolute_import
from spidermon import MonitorSuite


from .cases import *


class EmptySuite(MonitorSuite):
    pass


class Suite01(MonitorSuite):
    monitors = [Monitor01]


class Suite02(MonitorSuite):
    monitors = [Suite01, Monitor02]


class Suite03(MonitorSuite):
    monitors = [Suite01, Suite02]


class Suite04(MonitorSuite):
    monitors = [Suite01, Suite02, Monitor01, Monitor02]
