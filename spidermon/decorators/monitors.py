from __future__ import absolute_import
from spidermon.core.options import MonitorOptions
from spidermon import settings
from spidermon.decorators import OptionsDecorator, DecoratorWithAttributes


class LevelDecorator(DecoratorWithAttributes):
    name = "level"
    attributes = {
        "high": OptionsDecorator.set_fixed_value(
            MonitorOptions, name, settings.MONITOR.LEVEL.HIGH
        ),
        "normal": OptionsDecorator.set_fixed_value(
            MonitorOptions, name, settings.MONITOR.LEVEL.NORMAL
        ),
        "low": OptionsDecorator.set_fixed_value(
            MonitorOptions, name, settings.MONITOR.LEVEL.LOW
        ),
    }


name = OptionsDecorator.set_value(MonitorOptions, "name")
description = OptionsDecorator.set_value(MonitorOptions, "description")
order = OptionsDecorator.set_value(MonitorOptions, "order")
level = LevelDecorator()
