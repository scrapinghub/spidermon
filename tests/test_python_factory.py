import json
from typing import Any

import pytest

from spidermon.core.monitors import Monitor
from spidermon.core.suites import MonitorSuite
from spidermon.exceptions import InvalidMonitor, NotConfigured
from spidermon.python.factory import (
    PythonExpressionsMonitor,
    create_monitor_class_from_dict,
    create_monitor_class_from_json,
)
from spidermon.runners import MonitorRunner


class ContextMonitor(PythonExpressionsMonitor):
    def get_context_data(self) -> dict[str, Any]:
        return {"stats": {"foo": 1}}


def run_monitor_class(monitor_class: type[Monitor]) -> dict[str, tuple[Any, Any]]:
    suite = MonitorSuite(monitors=[monitor_class])
    result = MonitorRunner().run(suite)
    return {r.item.method_name: (r.status, r.reason) for r in result.monitor_results}


def test_default_get_context_data_is_not_configured() -> None:
    monitor_class = create_monitor_class_from_dict(
        {"name": "n", "tests": [{"name": "t", "expression": "1 == 1"}]},
    )
    method_name = next(name for name in vars(monitor_class) if name.startswith("test"))
    monitor = monitor_class(methodName=method_name)
    with pytest.raises(NotConfigured):
        monitor.get_context_data()


def test_create_monitor_class_from_dict_sets_name_and_description() -> None:
    monitor_class = create_monitor_class_from_dict(
        {
            "name": "My Monitor",
            "description": "My Description",
            "tests": [{"name": "t", "expression": "1 == 1"}],
        },
        ContextMonitor,
    )
    assert monitor_class.options.name == "My Monitor"
    assert monitor_class.options.description == "My Description"
    assert issubclass(monitor_class, ContextMonitor)


def test_create_monitor_class_from_dict_rejects_unrelated_monitor_class() -> None:
    class Unrelated:
        pass

    with pytest.raises(InvalidMonitor):
        create_monitor_class_from_dict(
            {"name": "n", "tests": [{"name": "t", "expression": "1 == 1"}]},
            Unrelated,  # type: ignore[arg-type]
        )


def test_create_monitor_class_from_json_matches_from_dict() -> None:
    definition = {
        "name": "My Monitor",
        "tests": [{"name": "t", "expression": "stats['foo'] == 1"}],
    }
    from_dict = create_monitor_class_from_dict(definition, ContextMonitor)
    from_json = create_monitor_class_from_json(json.dumps(definition), ContextMonitor)
    assert run_monitor_class(from_dict) == run_monitor_class(from_json)


def test_passing_expression_is_reported_as_success() -> None:
    monitor_class = create_monitor_class_from_dict(
        {
            "name": "n",
            "tests": [{"name": "positive", "expression": "stats['foo'] > 0"}],
        },
        ContextMonitor,
    )
    results = run_monitor_class(monitor_class)
    status, _reason = results["positive"]
    assert status == "OK"


def test_failing_expression_uses_default_message() -> None:
    monitor_class = create_monitor_class_from_dict(
        {
            "name": "n",
            "tests": [{"name": "negative", "expression": "stats['foo'] < 0"}],
        },
        ContextMonitor,
    )
    results = run_monitor_class(monitor_class)
    status, reason = results["negative"]
    assert status == "FAIL"
    assert "stats['foo'] < 0" in reason


def test_failing_expression_uses_custom_fail_reason() -> None:
    monitor_class = create_monitor_class_from_dict(
        {
            "name": "n",
            "tests": [
                {
                    "name": "negative",
                    "expression": "stats['foo'] < 0",
                    "fail_reason": "'foo should be negative, was ' + str(stats['foo'])",
                },
            ],
        },
        ContextMonitor,
    )
    results = run_monitor_class(monitor_class)
    status, reason = results["negative"]
    assert status == "FAIL"
    assert "foo should be negative, was 1" in reason


def test_multiple_tests_get_unique_method_names() -> None:
    monitor_class = create_monitor_class_from_dict(
        {
            "name": "n",
            "tests": [
                {"expression": "1 == 1"},
                {"expression": "2 == 2"},
            ],
        },
        ContextMonitor,
    )
    results = run_monitor_class(monitor_class)
    assert len(results) == 2
    assert all(status == "OK" for status, _ in results.values())
