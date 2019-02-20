from __future__ import absolute_import
import six

import inspect

from spidermon.exceptions import (
    InvalidMonitor,
    InvalidMonitorClass,
    InvalidMonitorTuple,
)
from .monitors import Monitor
from .actions import Action


class MonitorFactory(object):
    @classmethod
    def load_monitor(cls, monitor, name=None):
        from .suites import MonitorSuite

        if inspect.isclass(monitor):
            return cls.load_monitor_from_class(monitor_class=monitor, name=name)
        elif isinstance(monitor, tuple):
            return cls.load_monitor_from_tuple(monitor_tuple=monitor)
        elif isinstance(monitor, (Monitor, MonitorSuite)):
            return monitor
        cls.raise_invalid_monitor()

    @classmethod
    def load_monitor_from_class(cls, monitor_class, name=None):
        from .suites import MonitorSuite

        if issubclass(monitor_class, Monitor):
            from spidermon.loaders import MonitorLoader

            loader = MonitorLoader()
            monitor = loader.load_suite_from_monitor(
                monitor_class=monitor_class, name=name
            )
        elif issubclass(monitor_class, MonitorSuite):
            monitor = monitor_class(name=name)
        else:
            cls.raise_invalid_class()
        return cls.load_monitor(monitor=monitor, name=name)

    @classmethod
    def load_monitor_from_tuple(cls, monitor_tuple):
        if len(monitor_tuple) != 2:
            cls.raise_invalid_tuple()
        name, monitor = monitor_tuple
        if not isinstance(name, six.string_types):
            cls.raise_invalid_tuple()
        return cls.load_monitor(monitor=monitor, name=name)

    @classmethod
    def raise_invalid_monitor(cls):
        raise InvalidMonitor(
            "Wrong Monitor definition, it should be:\n"
            "- an instance of a Monitor/MonitorSuite object.\n"
            "- a subclass of Monitor/MonitorSuite.\n"
            "- a tuple with the format (name, monitor).\n"
            "- a string containing an evaluable python expression."
        )

    @classmethod
    def raise_invalid_class(cls):
        raise InvalidMonitorClass(
            "Wrong Monitor class definition, it should be "
            "an instance of a Monitor/MonitorSuite object."
        )

    @classmethod
    def raise_invalid_tuple(cls):
        raise InvalidMonitorTuple(
            "Wrong Monitor tuple definition, it should be "
            "a tuple with the format (name, monitor)"
        )


class ActionFactory(object):
    @classmethod
    def load_action(cls, action, crawler=None):
        if inspect.isclass(action):
            return cls.load_action_from_class(action_class=action, crawler=crawler)
        elif isinstance(action, Action):
            return action
        cls.raise_invalid_action()

    @classmethod
    def load_action_from_class(cls, action_class, crawler=None):
        if not issubclass(action_class, Action):
            cls.raise_invalid_class()
        if crawler and hasattr(action_class, "from_crawler"):
            return action_class.from_crawler(crawler)
        else:
            return action_class()

    @classmethod
    def raise_invalid_action(cls):
        raise Exception
        raise InvalidMonitor(
            "Wrong Monitor definition, it should be:\n"
            "- an instance of a Monitor/MonitorSuite object.\n"
            "- a subclass of Monitor/MonitorSuite.\n"
            "- a tuple with the format (name, monitor).\n"
            "- a string containing an evaluable python expression."
        )

    @classmethod
    def raise_invalid_class(cls):
        raise Exception
        raise InvalidMonitorClass(
            "Wrong Monitor class definition, it should be "
            "an instance of a Monitor/MonitorSuite object."
        )
