import inspect
from unittest import TestLoader
from functools import cmp_to_key as _cmp_to_key

from .monitors import Monitor
from .suites import MonitorSuite
from .exceptions import InvalidMonitor


class MonitorLoader(TestLoader):
    def load_suite_from_monitor(self, monitor):
        if not (inspect.isclass(monitor) and issubclass(monitor, Monitor)):
            raise InvalidMonitor('monitor must be a class subclassing Monitor')
        test_function_names = self.get_testcase_names(monitor)
        if not test_function_names and hasattr(monitor, 'runTest'):
            test_function_names = ['runTest']
        loaded_suite = MonitorSuite(map(monitor, test_function_names))
        return loaded_suite

    def get_testcase_names(self, monitor_class):
        def is_test_method(attrname, class_name=monitor_class, prefix=self.testMethodPrefix):
            return attrname.startswith(prefix) and \
                hasattr(getattr(class_name, attrname), '__call__')
        test_function_names = filter(is_test_method, dir(monitor_class))
        if self.sortTestMethodsUsing:
            test_function_names.sort(key=_cmp_to_key(self.sortTestMethodsUsing))
        return test_function_names

