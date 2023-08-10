import operator
import logging

from spidermon import Monitor
from spidermon.exceptions import NotConfigured

from ...monitors.mixins.spider import SpiderMonitorMixin

logger = logging.getLogger(__name__)


class BaseScrapyMonitor(Monitor, SpiderMonitorMixin):
    """
    Monitor can be skipped based on conditions given in the settings.
    The purpose is to skip a monitor based on stat value or any custom
    function. A scenario could be skipping the Field Coverage Monitor
    when a spider produced no items. Following is a code block of
    examples of how we can configure the skip rules in settings.

    Example #1: skip rules based on stat values
    .. code-block:: python
        class QuotesSpider(scrapy.Spider):
            name = "quotes"
            custom_settings = {
                "SPIDERMON_FIELD_COVERAGE_RULES": {
                    "dict/quote": 1,
                    "dict/author": 1,
                },
                "SPIDERMON_MONITOR_SKIPPING_RULES": {
                    "Field Coverage Monitor": [["item_scraped_count", "==", 0]],
                }
            }

    Example #2: skip rules based on a custom function
    .. code-block:: python

        def skip_function(monitor):
            return "item_scraped_count" not in monitor.data.stats

        class QuotesSpider(scrapy.Spider):
            name = "quotes"

            custom_settings = {
                "SPIDERMON_FIELD_COVERAGE_RULES": {
                    "dict/quote": 1,
                    "dict/author": 1,
                },
                "SPIDERMON_MONITOR_SKIPPING_RULES": {
                    "Field Coverage Monitor": [skip_function],
                }
            }
    """

    longMessage = False
    ops = {
        ">": operator.gt,
        ">=": operator.ge,
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
    }

    @property
    def monitor_description(self):
        if self.__class__.__doc__:
            return self.__class__.__doc__.split("\n")[0]
        return super().monitor_description

    def run(self, result):
        if self.check_if_skip_rule_met():
            logger.info(f"Skipping {self.monitor_name} monitor")
            return

        return super().run(result)

    def check_if_skip_rule_met(self):
        if (
            hasattr(self, "skip_rules")
            and getattr(self, "monitor_name")
            and self.skip_rules.get(self.monitor_name)
        ):
            skip_rules = self.skip_rules[self.monitor_name]
            for rule in skip_rules:
                if hasattr(rule, "__call__"):
                    if rule(self):
                        return True
                    continue
                stats_value = self.data.stats.get(rule[0], 0)
                if self.ops[rule[1]](stats_value, rule[2]):
                    return True

        return False


class BaseStatMonitor(BaseScrapyMonitor):
    """Base Monitor class for stat-related monitors.

    Create a monitor class inheriting from this class to have a custom
    monitor that validates numerical stats from your job execution
    against a configurable threshold. If this threshold is passed in
    via command line arguments (and not it the spider settings), the setting is read as a
    string and converted to ``threshold_datatype`` type (default is
    float).

    As an example, we will create a new monitor that will check if the
    value obtained in a job stat 'numerical_job_statistic' is greater than
    or equal to the value configured in ``CUSTOM_STAT_THRESHOLD`` project
    setting:

    .. code-block:: python

        class MyCustomStatMonitor(BaseStatMonitor):
            stat_name = "numerical_job_statistic"
            threshold_setting = "CUSTOM_STAT_THRESHOLD"
            assert_type = ">="

    For the ``assert_type`` property you can select one of the following:

    ==  =====================
    >   Greater than
    >=  Greater than or equal
    <   Less than
    <=  Less than or equal
    ==  Equal
    !=  Not equal
    ==  =====================

    Sometimes, we don't want a fixed threshold, but a dynamic based on more than
    one stat or getting data external from the job execution (e.g., you want the
    threshold to be related to another stat, or you want to get the value
    of a stat from a previous job).

    As an example, the following monitor will use as threshold the a variable number
    of errors allowed based on the number of items scraped. So this monitor will pass
    only if the number of errors is less than 1% of the number of items scraped:

    .. code-block:: python

        class MyCustomStatMonitor(BaseStatMonitor):
            stat_name = "log_count/ERROR"
            assert_type = "<"

            def get_threshold(self):
                item_scraped_count = self.stats.get("item_scraped_count")
                return item_scraped_count * 0.01

    By default, if the stat can't be found in job statistics, the monitor will fail.
    If you want the monitor to be skipped in that case, you should set ``fail_if_stat_missing``
    attribute as ``False``.


    The following monitor will not fail if the job doesn't have a ``numerical_job_statistic``
    value in its statistics:

    .. code-block:: python

        class MyCustomStatMonitor(BaseStatMonitor):
            stat_name = "numerical_job_statistic"
            threshold_setting = "CUSTOM_STAT_THRESHOLD"
            assert_type = ">="
            fail_if_stat_missing = False
    """

    fail_if_stat_missing = True
    threshold_datatype = float

    @property
    def _get_threshold_setting(self):
        datatype_to_function = {
            int: self.crawler.settings.getint,
            float: self.crawler.settings.getfloat,
        }

        return datatype_to_function[self.threshold_datatype]

    def run(self, result):
        has_threshold_config = any(
            [hasattr(self, "threshold_setting"), hasattr(self, "get_threshold")]
        )
        if not has_threshold_config:
            raise NotConfigured(
                f"{self.__class__.__name__} should include a a `threshold_setting` attribute "
                "to be configured in your project settings with the desired threshold "
                "or a `get_threshold` method that returns the desired threshold."
            )

        if (
            hasattr(self, "threshold_setting")
            and self.threshold_setting not in self.crawler.settings.attributes
        ):
            raise NotConfigured(
                f"Configure {self.threshold_setting} to your project "
                f"settings to use {self.monitor_name}."
            )

        return super().run(result)

    def _get_threshold_value(self):
        if hasattr(self, "get_threshold"):
            return self.get_threshold()
        return self._get_threshold_setting(self.threshold_setting)

    def test_stat_monitor(self):
        assertions = {
            ">": self.assertGreater,
            ">=": self.assertGreaterEqual,
            "<": self.assertLess,
            "<=": self.assertLessEqual,
            "==": self.assertEqual,
            "!=": self.assertNotEqual,
        }
        threshold = self._get_threshold_value()

        if self.stat_name not in self.stats:
            message = f"Unable to find '{self.stat_name}' in job stats."
            if self.fail_if_stat_missing:
                self.fail(message)
            else:
                self.skipTest(message)

        value = self.stats.get(self.stat_name)

        assertion_method = assertions.get(self.assert_type)
        assertion_method(
            value,
            threshold,
            msg=f"Expecting '{self.stat_name}' to be '{self.assert_type}' "
            f"to '{threshold}'. Current value: '{value}'",
        )
