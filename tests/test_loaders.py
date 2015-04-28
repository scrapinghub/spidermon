from spidermon import MonitorLoader, MonitorSuite
from spidermon.exceptions import InvalidMonitor

from fixtures.cases import *


@pytest.fixture
def loader():
    return MonitorLoader()


def test_loading(loader):
    _test_load(
        loader=loader,
        monitor_class=MonitorWithoutTests,
        expected_number_of_tests=0
    )
    _test_load(
        loader=loader,
        monitor_class=Monitor01,
        expected_number_of_tests=3
    )


def test_loading_errors(loader):
    with pytest.raises(InvalidMonitor):
        loader.load_suite_from_monitor(None)
    with pytest.raises(InvalidMonitor):
        loader.load_suite_from_monitor(10)
    with pytest.raises(InvalidMonitor):
        loader.load_suite_from_monitor(object)


def test_testcase_names(loader):
    _test_testcase_names(
        loader=loader,
        monitor_class=MonitorWithoutTests,
        expected_names=[]
    )
    _test_testcase_names(
        loader=loader,
        monitor_class=Monitor01,
        expected_names=[
            'test_a',
            'test_b',
            'test_c',
        ]
    )


def _test_testcase_names(loader, monitor_class, expected_names):
    names = loader.get_testcase_names(monitor_class)
    assert names == expected_names


def _test_load(loader, monitor_class, expected_number_of_tests):
    suite = loader.load_suite_from_monitor(monitor_class)
    assert isinstance(suite, MonitorSuite)
    assert suite.number_of_tests == expected_number_of_tests
    for test in suite:
        assert isinstance(test, Monitor)



