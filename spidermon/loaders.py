from __future__ import annotations

import inspect
from functools import cmp_to_key as _cmp_to_key
from unittest import TestLoader

from .core.monitors import Monitor
from .core.suites import MonitorSuite
from .exceptions import InvalidMonitor


class MonitorLoader(TestLoader):
    def load_suite_from_monitor(
        self,
        monitor_class: type[Monitor],
        name: str | None = None,
    ) -> MonitorSuite:
        if not (inspect.isclass(monitor_class) and issubclass(monitor_class, Monitor)):
            raise InvalidMonitor("monitor must be a class subclassing Monitor")
        test_function_names = self.get_testcase_names(monitor_class)
        if not test_function_names and hasattr(monitor_class, "runTest"):
            test_function_names = ["runTest"]
        monitors = [
            monitor_class(fn_name, name=name) for fn_name in test_function_names
        ]
        return MonitorSuite(
            monitors=monitors,
            order=monitor_class.options.order,
        )

    def get_testcase_names(self, monitor_class: type[Monitor]) -> list[str]:
        def is_test_method(
            attrname: str,
            class_name: type[Monitor] = monitor_class,
            prefix: str = self.testMethodPrefix,
        ) -> bool:
            return attrname.startswith(prefix) and callable(
                getattr(class_name, attrname)
            )

        test_function_names = list(filter(is_test_method, dir(monitor_class)))
        if self.sortTestMethodsUsing is not None:
            test_function_names.sort(key=_cmp_to_key(self.sortTestMethodsUsing))
        return test_function_names

    # TODO: hide methods?
