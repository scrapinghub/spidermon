from collections import OrderedDict


class TestCaseMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        test_methods = mcs.collect_test_methods(bases, attrs)
        cls = super(TestCaseMetaclass, mcs).__new__(mcs, name, bases, attrs)
        cls._tests = test_methods
        return cls

    @classmethod
    def collect_test_methods(mcs, bases, attrs):
        test_methods = {}

        # get base test methods
        for base in reversed(bases):
            if hasattr(base, '_tests'):
                test_methods.update(base._tests)

        # get class test methods
        for attr_name, attr in attrs.items():
            if hasattr(attr, '__call__') and attr_name.startswith('test_'):
                test_methods[attr_name] = attr

        return OrderedDict(sorted(test_methods.items()))


class TestCase(object):
    __metaclass__ = TestCaseMetaclass

    def __init__(self):
        self.stats = None

    def get_test_methods(self):
        return self._tests

    def init_context(self, stats):
        self.stats = stats

    def setUp(self):
        pass

    def tearDown(self):
        pass
