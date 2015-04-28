import pytest

from spidermon import MonitorLoader, MonitorSuite
from spidermon.exceptions import InvalidMonitor

from fixtures.cases import *


@pytest.fixture
def loader():
    return MonitorLoader()


def test_loading(loader):
    _check_suite(
        suite=loader.load_suite_from_monitor(EmptyMonitor),
        expected_number_of_tests=0
    )
    _check_suite(
        suite=loader.load_suite_from_monitor(Monitor01),
        expected_number_of_tests=3
    )
    _check_suite(
        suite=loader.load_suite_from_monitor(Monitor02),
        expected_number_of_tests=2
    )


def test_loading_errors(loader):
    with pytest.raises(InvalidMonitor):
        loader.load_suite_from_monitor(None)
    with pytest.raises(InvalidMonitor):
        loader.load_suite_from_monitor(10)
    with pytest.raises(InvalidMonitor):
        loader.load_suite_from_monitor(object)


def test_testcase_names(loader):
    _check_testcase_names(
        loader=loader,
        monitor_class=EmptyMonitor,
        expected_names=[]
    )
    _check_testcase_names(
        loader=loader,
        monitor_class=Monitor01,
        expected_names=[
            'test_a',
            'test_b',
            'test_c',
        ]
    )
    _check_testcase_names(
        loader=loader,
        monitor_class=Monitor02,
        expected_names=[
            'test_d',
            'test_e',
        ]
    )


def _check_testcase_names(loader, monitor_class, expected_names):
    names = loader.get_testcase_names(monitor_class)
    assert names == expected_names


def _check_suite(suite, expected_number_of_tests):
    assert isinstance(suite, MonitorSuite)
    assert suite.number_of_tests == expected_number_of_tests
    for test in suite:
        assert isinstance(test, Monitor)



