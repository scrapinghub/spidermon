import operator

import pytest

pytest.importorskip("scrapy")

from spidermon import MonitorSuite, settings
from spidermon.contrib.scrapy.monitors import BaseScrapyMonitor, ItemCountMonitor

ops = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}


def always_skip(monitor):
    return True


def never_skip(monitor):
    return False


class MultiCheckMonitor(BaseScrapyMonitor):
    def test_one(self):
        pass

    def test_two(self):
        self.fail("boom")


@pytest.mark.parametrize(
    ("value", "threshold", "expected_status", "rules"),
    [
        (100, 100, settings.MONITOR.STATUS.SUCCESS, None),
        (1000, 1, settings.MONITOR.STATUS.SUCCESS, None),
        (1, 0, settings.MONITOR.STATUS.SUCCESS, None),
        (0, 10, None, {"Extracted Items Monitor": [["item_scraped_count", "<", 1]]}),
        (50, 100, None, {"Extracted Items Monitor": [["item_scraped_count", "<", 60]]}),
        (
            99,
            100,
            settings.MONITOR.STATUS.FAILURE,
            {"Extracted Items Monitor": [["item_scraped_count", "<", 1]]},
        ),
        (
            101,
            100,
            settings.MONITOR.STATUS.SUCCESS,
            {"Extracted Items Monitor": [["item_scraped_count", "<", 1]]},
        ),
    ],
)
def test_skipping_rule_on_stats_value(
    make_data, value, threshold, expected_status, rules
):
    data = make_data(
        {
            ItemCountMonitor.threshold_setting: threshold,
            "SPIDERMON_MONITOR_SKIPPING_RULES": rules,
        },
    )

    runner = data.pop("runner")
    data["stats"][ItemCountMonitor.stat_name] = value
    runner.run(MonitorSuite(monitors=[ItemCountMonitor]), **data)

    if rules:
        rule = rules["Extracted Items Monitor"][0]
        if ops[rule[1]](value, rule[2]):  # Monitor didn't run
            assert runner.result.monitor_results == []
            return

    assert runner.result.monitor_results[0].status == expected_status


@pytest.mark.parametrize(
    ("value", "threshold", "expected_status", "rules"),
    [
        (0, 10, None, {"Extracted Items Monitor": [always_skip]}),
        (
            50,
            100,
            settings.MONITOR.STATUS.FAILURE,
            {"Extracted Items Monitor": [never_skip]},
        ),
    ],
)
def test_skipping_rule_on_callable_function(
    make_data, value, threshold, expected_status, rules
):
    data = make_data(
        {
            ItemCountMonitor.threshold_setting: threshold,
            "SPIDERMON_MONITOR_SKIPPING_RULES": rules,
        },
    )

    runner = data.pop("runner")
    data["stats"][ItemCountMonitor.stat_name] = value
    runner.run(MonitorSuite(monitors=[ItemCountMonitor]), **data)

    if rules:
        rule = rules["Extracted Items Monitor"][0]
        if rule.__name__ == "always_skip":
            assert runner.result.monitor_results == []
            return

    assert runner.result.monitor_results[0].status == expected_status


def test_skipping_rule_by_method_name(make_data):
    data = make_data(
        {
            "SPIDERMON_MONITOR_SKIPPING_RULES": {
                "MultiCheckMonitor/test_two": [always_skip],
            },
        },
    )
    runner = data.pop("runner")
    suite = MonitorSuite(monitors=[MultiCheckMonitor])
    runner.run(suite, **data)

    results = runner.result.monitor_results
    assert len(results) == 1
    assert results[0].monitor.name == "MultiCheckMonitor/test_one"
    assert results[0].status == settings.MONITOR.STATUS.SUCCESS
