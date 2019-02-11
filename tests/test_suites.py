from __future__ import absolute_import
import pytest

from spidermon import MonitorSuite
from spidermon.exceptions import (
    InvalidMonitor,
    InvalidMonitorIterable,
    InvalidMonitorClass,
    InvalidMonitorTuple,
    NotAllowedMethod,
)

from .fixtures.suites import *


class SuiteDefinition(object):
    def __init__(self, suite_class, monitors=None, expected_number_of_monitors=0):
        self.suite_class = suite_class
        self.monitors = monitors or []
        self.expected_number_of_monitors = expected_number_of_monitors


CLASS_SUITE_DEFINITIONS = [
    # ---------------------------------------------------------------------------------
    #               suite_class    monitors               expected_number_of_monitors
    # ---------------------------------------------------------------------------------
    # no monitors
    SuiteDefinition(EmptySuite, [], 0),
    SuiteDefinition(Suite01, [], 3),
    SuiteDefinition(Suite02, [], 5),
    SuiteDefinition(Suite03, [], 8),
    SuiteDefinition(Suite04, [], 13),
    # monitors as classes
    SuiteDefinition(EmptySuite, [EmptyMonitor], 0),
    SuiteDefinition(EmptySuite, [Monitor01], 3),
    SuiteDefinition(EmptySuite, [Monitor02], 2),
    SuiteDefinition(EmptySuite, [Monitor01, Monitor02], 5),
    SuiteDefinition(EmptySuite, [Suite01], 3),
    SuiteDefinition(EmptySuite, [Suite01, Suite02], 8),
    SuiteDefinition(EmptySuite, [Suite01, Suite02, Monitor01, Monitor02], 13),
    SuiteDefinition(Suite01, [Suite01, Suite02, Monitor01, Monitor02], 16),
    SuiteDefinition(Suite02, [Suite01, Suite02, Monitor01, Monitor02], 18),
    SuiteDefinition(Suite03, [Suite01, Suite02, Monitor01, Monitor02], 21),
    SuiteDefinition(Suite04, [Suite01, Suite02, Monitor01, Monitor02], 26),
    # monitors as instances
    SuiteDefinition(EmptySuite, [Suite01()], 3),
    SuiteDefinition(EmptySuite, [Suite02()], 5),
    SuiteDefinition(EmptySuite, [Suite03()], 8),
    SuiteDefinition(EmptySuite, [Suite04()], 13),
    SuiteDefinition(EmptySuite, [Suite01(), Suite02(), Suite03(), Suite04()], 29),
    # monitors as tuples
    SuiteDefinition(EmptySuite, [("M1", Monitor01)], 3),
    SuiteDefinition(EmptySuite, [("M1", Monitor01), ("M2", Monitor02)], 5),
    SuiteDefinition(EmptySuite, [("S", Suite04)], 13),
]
INVALID_SUITE_DEFINITION_NON_ITERABLE = SuiteDefinition(EmptySuite, 10)
INVALID_SUITE_DEFINITION_NONE = SuiteDefinition(EmptySuite, [None])
INVALID_SUITE_DEFINITION_NUMBER = SuiteDefinition(EmptySuite, [10])
INVALID_SUITE_DEFINITION_CLASS = SuiteDefinition(EmptySuite, [object])
INVALID_SUITE_DEFINITION_TUPLE1 = SuiteDefinition(EmptySuite, [(1,)])
INVALID_SUITE_DEFINITION_TUPLE3 = SuiteDefinition(EmptySuite, [(1, 2, 3)])
INVALID_SUITE_DEFINITION_TUPLE2_WRONG1 = SuiteDefinition(EmptySuite, [(1, 2)])
INVALID_SUITE_DEFINITION_TUPLE2_WRONG2 = SuiteDefinition(EmptySuite, [("A", 2)])

INVALID_SUITE_DEFINITIONS = [
    # --------------------------------------------------------------
    # definition                                raises
    # --------------------------------------------------------------
    (INVALID_SUITE_DEFINITION_NONE, InvalidMonitor),
    (INVALID_SUITE_DEFINITION_NUMBER, InvalidMonitor),
    (INVALID_SUITE_DEFINITION_CLASS, InvalidMonitorClass),
    (INVALID_SUITE_DEFINITION_TUPLE1, InvalidMonitorTuple),
    (INVALID_SUITE_DEFINITION_TUPLE3, InvalidMonitorTuple),
    (INVALID_SUITE_DEFINITION_TUPLE2_WRONG1, InvalidMonitorTuple),
    (INVALID_SUITE_DEFINITION_TUPLE2_WRONG2, InvalidMonitor),
]


def test_creation_error_non_iterable():
    with pytest.raises(InvalidMonitorIterable):
        _test_creation_from_init(INVALID_SUITE_DEFINITION_NON_ITERABLE)
    with pytest.raises(InvalidMonitorIterable):
        _test_creation_from_add_monitors(INVALID_SUITE_DEFINITION_NON_ITERABLE)


def test_creation_error_invalid_from_init():
    for definition, exception_to_raise in INVALID_SUITE_DEFINITIONS:
        with pytest.raises(exception_to_raise):
            _test_creation_from_init(definition)


def test_creation_error_invalid_from_add_monitors():
    for definition, exception_to_raise in INVALID_SUITE_DEFINITIONS:
        with pytest.raises(exception_to_raise):
            _test_creation_from_add_monitors(definition)


def test_creation_error_invalid_from_add_monitor():
    for definition, exception_to_raise in INVALID_SUITE_DEFINITIONS:
        with pytest.raises(exception_to_raise):
            _test_creation_from_add_monitor(definition)


def test_creation_from_init():
    for definition in CLASS_SUITE_DEFINITIONS:
        _test_creation_from_init(definition)


def test_creation_from_add_monitors():
    for definition in CLASS_SUITE_DEFINITIONS:
        _test_creation_from_add_monitors(definition)


def test_creation_from_add_monitor():
    for definition in CLASS_SUITE_DEFINITIONS:
        _test_creation_from_add_monitor(definition)


def _test_creation_from_init(definition):
    suite = definition.suite_class(monitors=definition.monitors)
    check_suite(
        suite=suite, expected_number_of_monitors=definition.expected_number_of_monitors
    )


def test_not_allowed_methods():
    suite = EmptySuite()
    with pytest.raises(NotAllowedMethod):
        suite.addTest()
    with pytest.raises(NotAllowedMethod):
        suite.addTests()


def _test_creation_from_add_monitors(definition):
    suite = definition.suite_class()
    suite.add_monitors(definition.monitors)
    check_suite(
        suite=suite, expected_number_of_monitors=definition.expected_number_of_monitors
    )


def _test_creation_from_add_monitor(definition):
    suite = definition.suite_class()
    for monitor in definition.monitors:
        suite.add_monitor(monitor)
    check_suite(
        suite=suite, expected_number_of_monitors=definition.expected_number_of_monitors
    )


def check_suite(suite, expected_number_of_monitors):
    # print
    # print suite.debug_tree()
    # print
    assert isinstance(suite, MonitorSuite)
    assert suite.number_of_monitors == expected_number_of_monitors
    for monitor in suite:
        assert isinstance(monitor, (Monitor, MonitorSuite))
    all_monitors = suite.all_monitors
    assert len(all_monitors) == expected_number_of_monitors
    for test in all_monitors:
        assert isinstance(test, (Monitor, Monitor))
