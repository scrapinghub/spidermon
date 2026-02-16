# monitors.py
from spidermon import Monitor, MonitorSuite, monitors
from spidermon.contrib.actions.slack.notifiers import SendSlackMessageSpiderFinished
from spidermon.contrib.monitors.mixins import StatsMonitorMixin
from tutorial.actions import CloseSpiderAction


@monitors.name("Item count")
class ItemCountMonitor(Monitor):
    @monitors.name("Minimum items extracted")
    def test_minimum_number_of_items_extracted(self):
        minimum_threshold = 1000
        item_extracted = getattr(self.data.stats, "item_scraped_count", 0)
        self.assertFalse(
            item_extracted < minimum_threshold,
            msg=f"Extracted less than {minimum_threshold} items",
        )


@monitors.name("Item validation")
class ItemValidationMonitor(Monitor, StatsMonitorMixin):
    @monitors.name("No item validation errors")
    def test_no_item_validation_errors(self):
        validation_errors = getattr(
            self.data.stats,
            "spidermon/validation/fields/errors",
            0,
        )
        self.assertEqual(
            validation_errors,
            0,
            msg=f"Found validation errors in {validation_errors} fields",
        )


@monitors.name("Periodic job stats monitor")
class PeriodicJobStatsMonitor(Monitor, StatsMonitorMixin):
    @monitors.name("Maximum number of errors exceeded")
    def test_number_of_errors(self):
        accepted_num_errors = 20
        num_errors = self.data.stats.get("log_count/ERROR", 0)

        msg = "The job has exceeded the maximum number of errors"
        self.assertLessEqual(num_errors, accepted_num_errors, msg=msg)


class PeriodicMonitorSuite(MonitorSuite):
    monitors = [PeriodicJobStatsMonitor]
    monitors_failed_actions = [CloseSpiderAction]


class SpiderCloseMonitorSuite(MonitorSuite):
    monitors = [ItemCountMonitor, ItemValidationMonitor, PeriodicJobStatsMonitor]

    monitors_failed_actions = [SendSlackMessageSpiderFinished]
