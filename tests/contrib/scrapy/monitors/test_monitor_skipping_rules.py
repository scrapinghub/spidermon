import operator
import pytest
from spidermon.contrib.scrapy.monitors import ItemCountMonitor
from spidermon import settings
from scrapy.utils.test import get_crawler
from spidermon.contrib.scrapy.monitors.suites import SpiderCloseMonitorSuite


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


class monitorSuite(SpiderCloseMonitorSuite):
    monitors = [ItemCountMonitor]


@pytest.mark.parametrize(
    "value,threshold,expected_status,rules",
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
        }
    )

    settings = {"SPIDERMON_MONITOR_SKIPPING_RULES": rules}
    crawler = get_crawler(settings_dict=settings)
    new_suite = monitorSuite(crawler=crawler)

    runner = data.pop("runner")
    data["stats"][ItemCountMonitor.stat_name] = value
    runner.run(new_suite, **data)

    if rules:
        rule = rules["Extracted Items Monitor"][0]
        ops[rule[1]](value, rule[2])
        if ops[rule[1]](value, rule[2]):  # Monitor didn't ran
            assert runner.result.monitor_results == []
            return

    assert runner.result.monitor_results[0].status == expected_status


@pytest.mark.parametrize(
    "value,threshold,expected_status,rules",
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
        }
    )

    settings = {"SPIDERMON_MONITOR_SKIPPING_RULES": rules}
    crawler = get_crawler(settings_dict=settings)
    new_suite = monitorSuite(crawler=crawler)

    runner = data.pop("runner")
    data["stats"][ItemCountMonitor.stat_name] = value
    runner.run(new_suite, **data)

    if rules:
        rule = rules["Extracted Items Monitor"][0]
        if rule.__name__ == "always_skip":
            assert runner.result.monitor_results == []
            return

    assert runner.result.monitor_results[0].status == expected_status
