# tutorial/monitors.py
from spidermon import monitors, MonitorSuite, Monitor
from spidermon.exceptions import NotConfigured
from ..monitors.mixins.spider import SpiderMonitorMixin

SPIDERMON_MIN_ITEMS_SETTING = 'SPIDERMON_MIN_ITEMS'
SPIDERMON_MAX_ERROR_SETTING = 'SPIDERMON_MAX_ITEMS'
SPIDERMON_EXPECTED_FINISH_REASONS = 'SPIDERMON_EXPECTED_FINISH_REASONS'


class BaseScrapyMonitor(Monitor, SpiderMonitorMixin):
    longMessage = False

    def get_settings(self, name, default=None):
        """ Return a settings prioritized by:
            1. {name} as a spider attribute if not found
            2. {name}.upper() in the settings object
        """
        settings_value = self.crawler.settings.get(name.upper())
        if type(settings_value) == dict:
            settings_value = settings_value.get(self.spider.name, None)
        spider_value = getattr(self.spider, name.lower(), None)
        return spider_value or settings_value or default


@monitors.name('Extracted Items Monitor')
class ItemCountMonitor(BaseScrapyMonitor):
    """ Check for the minimum number of extracted items """

    @monitors.name('Should extract the minimum amount of items')
    def test_minimum_number_of_items(self):
        minimum_threshold = self.get_settings(SPIDERMON_MIN_ITEMS_SETTING)
        if not minimum_threshold:
            raise NotConfigured('You should specify a minimum number of items '
                                'to check against.')

        item_extracted = getattr(self.stats, 'item_scraped_count', 0)
        msg = 'Extracted {} items, the expected minimum is {}'.format(
            item_extracted, minimum_threshold)
        self.assertTrue(
            item_extracted >= minimum_threshold, msg=msg
        )


@monitors.name('Log Monitor')
class LogMonitor(BaseScrapyMonitor):
    """ Check for errors in logs """

    @monitors.name('Should not have any errors')
    def test_should_not_have_errors(self):
        errors_threshold = self.get_settings(SPIDERMON_MAX_ERROR_SETTING, 0)
        no_of_errors = self.stats.get('log_count/ERROR', 0)
        msg = 'Found {} errors in log, maximum expected is '\
              '{}'.format(no_of_errors, errors_threshold)
        self.assertTrue(no_of_errors <= errors_threshold, msg=msg)


@monitors.name('Finish Reason Monitor')
class FinishReasonMonitor(BaseScrapyMonitor):
    """ Check for finished reason in a job """

    @monitors.name('Should have the expected finished reason(s)')
    def test_should_not_have_errors(self):
        expected_reasons = self.get_settings(
            SPIDERMON_EXPECTED_FINISH_REASONS, ('finished', ))
        finished_reason = self.stats.get('finish_reason')
        msg = 'Finished with "{}" the expected reasons are {}'.format(
                finished_reason, expected_reasons)
        self.assertTrue(finished_reason in expected_reasons, msg=msg)


class SpiderCloseMonitorSuite(MonitorSuite):

    monitors = [
        ItemCountMonitor,
        LogMonitor,
        FinishReasonMonitor,
    ]
