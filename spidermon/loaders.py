from __future__ import absolute_import
import inspect
from unittest import TestLoader
from functools import cmp_to_key as _cmp_to_key

from .core.monitors import Monitor
from .core.suites import MonitorSuite
from .exceptions import InvalidMonitor
from six.moves import filter


class MonitorLoader(TestLoader):
    def load_suite_from_monitor(self, monitor_class, name=None):
        if not (inspect.isclass(monitor_class) and issubclass(monitor_class, Monitor)):
            raise InvalidMonitor("monitor must be a class subclassing Monitor")
        test_function_names = self.get_testcase_names(monitor_class)
        if not test_function_names and hasattr(monitor_class, "runTest"):
            test_function_names = ["runTest"]
        monitors = [
            monitor_class(fn_name, name=name) for fn_name in test_function_names
        ]
        loaded_suite = MonitorSuite(
            monitors=monitors, order=monitor_class.options.order
        )
        return loaded_suite

    def get_testcase_names(self, monitor_class):
        def is_test_method(
            attrname, class_name=monitor_class, prefix=self.testMethodPrefix
        ):
            return attrname.startswith(prefix) and hasattr(
                getattr(class_name, attrname), "__call__"
            )

        test_function_names = list(filter(is_test_method, dir(monitor_class)))
        if self.sortTestMethodsUsing:
            test_function_names.sort(key=_cmp_to_key(self.sortTestMethodsUsing))
        return test_function_names

    # TODO: hide methods?
