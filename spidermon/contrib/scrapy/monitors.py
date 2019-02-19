from spidermon import monitors, MonitorSuite, Monitor
from spidermon.exceptions import NotConfigured
from ..monitors.mixins.spider import SpiderMonitorMixin

SPIDERMON_MIN_ITEMS = 'SPIDERMON_MIN_ITEMS'
SPIDERMON_MAX_ERRORS = 'SPIDERMON_MAX_ERRORS'
SPIDERMON_EXPECTED_FINISH_REASONS = 'SPIDERMON_EXPECTED_FINISH_REASONS'
SPIDERMON_UNWANTED_HTTP_CODES = 'SPIDERMON_UNWANTED_HTTP_CODES'


class BaseScrapyMonitor(Monitor, SpiderMonitorMixin):
    longMessage = False

    @property
    def monitor_description(self):
        if self.__class__.__doc__:
            return self.__class__.__doc__.split('\n')[0]
        return super(BaseScrapyMonitor, self).monitor_description


@monitors.name('Extracted Items Monitor')
class ItemCountMonitor(BaseScrapyMonitor):
    """Check if spider extracted the minimum number of items.

    You can configure it using ``SPIDERMON_MIN_ITEMS`` setting.
    There's **NO** default value for this setting, if you try to use this
    monitor without setting it, it'll raise a ``NotConfigured`` exception.
    """
    def run(self, result):
        self.minimum_threshold = self.crawler.settings.getint(
            SPIDERMON_MIN_ITEMS, 0)
        if not self.minimum_threshold:
            raise NotConfigured('You should specify a minimum number of items '
                                'to check against.')
        return super(ItemCountMonitor, self).run(result)

    @monitors.name('Should extract the minimum amount of items')
    def test_minimum_number_of_items(self):
        item_extracted = getattr(self.stats, 'item_scraped_count', 0)
        msg = 'Extracted {} items, the expected minimum is {}'.format(
            item_extracted, self.minimum_threshold)
        self.assertTrue(
            item_extracted >= self.minimum_threshold, msg=msg
        )


@monitors.name('Error Count Monitor')
class ErrorCountMonitor(BaseScrapyMonitor):
    """Check for errors in the spider log.

    You can configure the expected number of ERROR log messages using
    ``SPIDERMON_MAX_ERRORS``. The default is ``0``."""
    @monitors.name('Should not have any errors')
    def test_max_errors_in_log(self):
        errors_threshold = self.crawler.settings.getint(
            SPIDERMON_MAX_ERRORS, 0)
        no_of_errors = self.stats.get('log_count/ERROR', 0)
        msg = 'Found {} errors in log, maximum expected is '\
              '{}'.format(no_of_errors, errors_threshold)
        self.assertTrue(no_of_errors <= errors_threshold, msg=msg)


@monitors.name('Finish Reason Monitor')
class FinishReasonMonitor(BaseScrapyMonitor):
    """Check if a job has a expected finish reason.

    You can configure the expected reason with the
    ``SPIDERMON_EXPECTED_FINISH_REASONS``, it should be an ``iterable`` of
    valid finish reasons.

    The default value of this settings is: ``['finished', ]``."""
    @monitors.name('Should have the expected finished reason(s)')
    def test_should_finish_with_expected_reason(self):
        expected_reasons = self.crawler.settings.getlist(
            SPIDERMON_EXPECTED_FINISH_REASONS, ('finished', ))
        finished_reason = self.stats.get('finish_reason')
        msg = 'Finished with "{}" the expected reasons are {}'.format(
                finished_reason, expected_reasons)
        self.assertTrue(finished_reason in expected_reasons, msg=msg)


@monitors.name('Unwanted HTTP codes monitor')
class UnwantedHTTPCodesMonitor(BaseScrapyMonitor):
    """Check for maximum number of unwanted HTTP codes.

    You can configure a ``dict`` of unwanted HTTP codes with
    ``SPIDERMON_UNWANTED_HTTP_CODES`` the default value is::

        DEFAULT_ERROR_CODES = {
            code: 10
            for code in [400, 407, 429, 500, 502, 503, 504, 523, 540, 541]}
    """
    DEFAULT_ERROR_CODES = {
        code: 10
        for code in [400, 407, 429, 500, 502, 503, 504, 523, 540, 541]}

    @monitors.name('Should not hit the limit of unwanted http status')
    def test_check_unwanted_http_codes(self):
        error_codes = self.crawler.settings.getdict(
            SPIDERMON_UNWANTED_HTTP_CODES, self.DEFAULT_ERROR_CODES)
        for code, max_errors in error_codes.items():
            code = int(code)
            count = self.stats.get(
                'downloader/response_status_count/{}'.format(code), 0)
            msg = 'Found {} Responses with status code={} - '\
                  'This exceed the limit of {}'.format(count, code, max_errors)
            self.assertTrue(count <= max_errors, msg=msg)


class SpiderCloseMonitorSuite(MonitorSuite):
    """This Monitor Suite implements the following monitors:

    * :class:`ItemCountMonitor`
    * :class:`ErrorCountMonitor`
    * :class:`FinishReasonMonitor`
    * :class:`UnwantedHTTPCodesMonitor`

    You can easily enable this monitor *after* enabling Spidermon::

            SPIDERMON_SPIDER_CLOSE_MONITORS = (
                'spidermon.contrib.scrapy.monitors.SpiderCloseMonitorSuite',
            )
    """
    monitors = [
        ItemCountMonitor,
        ErrorCountMonitor,
        FinishReasonMonitor,
        UnwantedHTTPCodesMonitor,
    ]
