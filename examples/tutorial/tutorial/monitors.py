# monitors.py
from spidermon import Monitor, MonitorSuite, monitors
from spidermon.contrib.actions.slack.notifiers import SendSlackMessageSpiderFinished
from spidermon.contrib.monitors.mixins import StatsMonitorMixin


@monitors.name("Item count")
class ItemCountMonitor(Monitor):
    @monitors.name("Minimum items extracted")
    def test_minimum_number_of_items_extracted(self):
        minimum_threshold = 1000
        item_extracted = getattr(self.data.stats, "item_scraped_count", 0)
        self.assertFalse(
            item_extracted < minimum_threshold,
            msg="Extracted less than {} items".format(minimum_threshold),
        )


@monitors.name("Item validation")
class ItemValidationMonitor(Monitor, StatsMonitorMixin):
    @monitors.name("No item validation errors")
    def test_no_item_validation_errors(self):
        validation_errors = getattr(
            self.data.stats, "spidermon/validation/fields/errors", 0
        )
        self.assertEqual(
            validation_errors,
            0,
            msg="Found validation errors in {} fields".format(validation_errors),
        )

        self.data.stats


class SpiderCloseMonitorSuite(MonitorSuite):
    monitors = [ItemCountMonitor, ItemValidationMonitor]

    monitors_failed_actions = [SendSlackMessageSpiderFinished]
