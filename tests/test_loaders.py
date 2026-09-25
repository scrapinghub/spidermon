import pytest

from spidermon import Monitor, MonitorLoader
from spidermon.exceptions import InvalidMonitor

from .fixtures.cases import EmptyMonitor, Monitor01, Monitor02
from .test_suites import check_suite


@pytest.fixture
def loader() -> MonitorLoader:
    return MonitorLoader()


def test_loading(loader: MonitorLoader) -> None:
    check_suite(
        suite=loader.load_suite_from_monitor(EmptyMonitor),
        expected_number_of_monitors=0,
    )
    check_suite(
        suite=loader.load_suite_from_monitor(Monitor01),
        expected_number_of_monitors=3,
    )
    check_suite(
        suite=loader.load_suite_from_monitor(Monitor02),
        expected_number_of_monitors=2,
    )


def test_loading_errors(loader: MonitorLoader) -> None:
    with pytest.raises(InvalidMonitor):
        loader.load_suite_from_monitor(None)  # type: ignore[arg-type]
    with pytest.raises(InvalidMonitor):
        loader.load_suite_from_monitor(10)  # type: ignore[arg-type]
    with pytest.raises(InvalidMonitor):
        loader.load_suite_from_monitor(object)  # type: ignore[arg-type]


def test_testcase_names(loader: MonitorLoader) -> None:
    _check_testcase_names(loader=loader, monitor_class=EmptyMonitor, expected_names=[])
    _check_testcase_names(
        loader=loader,
        monitor_class=Monitor01,
        expected_names=["test_a", "test_b", "test_c"],
    )
    _check_testcase_names(
        loader=loader,
        monitor_class=Monitor02,
        expected_names=["test_d", "test_e"],
    )


def _check_testcase_names(
    loader: MonitorLoader, monitor_class: type[Monitor], expected_names: list[str]
) -> None:
    names = loader.get_testcase_names(monitor_class)
    assert names == expected_names
