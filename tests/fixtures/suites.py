from collections.abc import Sequence
from typing import ClassVar

from spidermon import Monitor, MonitorSuite

from .cases import Monitor01, Monitor02


class EmptySuite(MonitorSuite):
    pass


class Suite01(MonitorSuite):
    monitors: ClassVar[
        Sequence[
            type[MonitorSuite | Monitor] | tuple[str, type[MonitorSuite | Monitor]]
        ]
    ] = [Monitor01]


class Suite02(MonitorSuite):
    monitors: ClassVar[
        Sequence[
            type[MonitorSuite | Monitor] | tuple[str, type[MonitorSuite | Monitor]]
        ]
    ] = [
        Suite01,
        Monitor02,
    ]


class Suite03(MonitorSuite):
    monitors: ClassVar[
        Sequence[
            type[MonitorSuite | Monitor] | tuple[str, type[MonitorSuite | Monitor]]
        ]
    ] = [
        Suite01,
        Suite02,
    ]


class Suite04(MonitorSuite):
    monitors: ClassVar[
        Sequence[
            type[MonitorSuite | Monitor] | tuple[str, type[MonitorSuite | Monitor]]
        ]
    ] = [
        Suite01,
        Suite02,
        Monitor01,
        Monitor02,
    ]
