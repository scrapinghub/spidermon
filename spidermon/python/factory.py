import json
from spidermon import Monitor
from spidermon.core.options import MonitorOptions
from spidermon.python import Interpreter


class PythonExpressionsMonitor(Monitor):
    _classes_counter = 0
    _test_methods_counter = 0
    _test_methods_prefix = 'test'

    @classmethod
    def generate_class_name(cls):
        cls._classes_counter += 1
        return '%s%d' % (cls.__name__, cls._classes_counter)

    @classmethod
    def generate_method_name(cls):
        cls._test_methods_counter += 1
        return '%s_python_expression_%d' % (cls._test_methods_prefix, cls._test_methods_counter)

    def get_context_data(self):
        return {
            'data': self.data,
        }


def create_monitor_class_from_json(monitor_json, monitor_class=None):
    monitor_dict = json.loads(monitor_json)
    return create_monitor_class_from_dict(monitor_dict, monitor_class)


def create_monitor_class_from_dict(monitor_dict, monitor_class=None):
    tests = []
    for test in monitor_dict.get('tests', []):
        tests.append((
            test['expression'],
            test.get('name', None),
            test.get('description', None),
            test.get('fail_reason', None),
        ))
    klass = _create_monitor_class(tests, monitor_class)
    name = monitor_dict.get('name', None)
    if name:
        klass.options.name = name
    description = monitor_dict.get('description', None)
    if name:
        klass.options.description = description
    return klass


def _create_monitor_class(expressions, monitor_class=None):
    monitor_class = monitor_class or PythonExpressionsMonitor
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
            self.assertTrue(bool(result),
                            msg=('Expression not safisfied: "%s"' % expression)
                            if not fail_reason else
                            fail_reason.format(**context))
    test_method = _test_method
    MonitorOptions.add_or_create(test_method)
    if name:
        test_method.options.name = name
    if description:
        test_method.options.description = description
    return test_method

