from __future__ import absolute_import
import json
from jsonschema import validate

from spidermon import Monitor
from spidermon.core.options import MonitorOptions
from spidermon.python import Interpreter, schemas
from spidermon.exceptions import InvalidMonitor, NotConfigured
from spidermon import settings


class PythonExpressionsMonitor(Monitor):
    _classes_counter = 0
    _test_methods_counter = 0
    _test_methods_prefix = "test"

    @classmethod
    def generate_class_name(cls):
        cls._classes_counter += 1
        return "%s%d" % (cls.__name__, cls._classes_counter)

    @classmethod
    def generate_method_name(cls):
        cls._test_methods_counter += 1
        return "%s_python_expression_%d" % (
            cls._test_methods_prefix,
            cls._test_methods_counter,
        )

    def get_context_data(self):
        raise NotConfigured("Context data needs to be set up")


def create_monitor_class_from_json(monitor_json, monitor_class=None):
    monitor_dict = json.loads(monitor_json)
    validate(monitor_dict, schemas.MONITOR_SCHEMA)
    return create_monitor_class_from_dict(monitor_dict, monitor_class)


def create_monitor_class_from_dict(monitor_dict, monitor_class=None):
    tests = []
    for test in monitor_dict.get("tests", []):
        tests.append(
            (
                test["expression"],
                test.get("name", None),
                test.get("description", None),
                test.get("fail_message", None),
            )
        )
    klass = _create_monitor_class(tests, monitor_class)
    klass.options.name = monitor_dict.get("name", settings.MONITOR.DEFAULT_NAME)
    klass.options.description = monitor_dict.get(
        "description", settings.MONITOR.DEFAULT_DESCRIPTION
    )
    return klass


def _create_monitor_class(expressions, monitor_class=None):
    monitor_class = monitor_class or PythonExpressionsMonitor
    if not issubclass(monitor_class, PythonExpressionsMonitor):
        msg = "Python expressions monitors must subclass PythonExpressionsMonitor"
        raise InvalidMonitor(msg)
    klass = type(monitor_class.generate_class_name(), (monitor_class,), {})
    for e in expressions:
        if isinstance(e, tuple):
            method = _create_test_method(*e)
        else:
            method = _create_test_method(e)
        setattr(klass, monitor_class.generate_method_name(), method)
    return klass


def _create_test_method(expression, name=None, description=None, fail_reason=None):
    def _test_method(self):
        interpreter = Interpreter()
        context = self.get_context_data()
        result = interpreter.eval(expression, context=context)
        if result is not None:
            self.assertTrue(
                bool(result),
                msg=('Expression not safisfied: "%s"' % expression)
                if not fail_reason
                else interpreter.eval(fail_reason, context=context),
            )

    test_method = _test_method
    MonitorOptions.add_or_create(test_method)
    test_method.options.name = name or settings.MONITOR.DEFAULT_NAME
    test_method.options.description = (
        description or settings.MONITOR.DEFAULT_DESCRIPTION
    )
    return test_method
