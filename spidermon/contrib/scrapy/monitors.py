# tutorial/monitors.py
from spidermon import monitors, MonitorSuite, Monitor
from spidermon.exceptions import NotConfigured
from ..monitors.mixins.spider import SpiderMonitorMixin

SPIDERMON_MIN_ITEMS = 'SPIDERMON_MIN_ITEMS'
SPIDERMON_MAX_ERROR = 'SPIDERMON_MAX_ITEMS'
SPIDERMON_EXPECTED_FINISH_REASONS = 'SPIDERMON_EXPECTED_FINISH_REASONS'
SPIDERMON_MAX_UNWANTED_HTTP_CODES = 'SPIDERMON_MAX_UNWANTED_HTTP_CODES'
SPIDERMON_UNWANTED_HTTP_CODES = 'SPIDERMON_UNWANTED_HTTP_CODES'


class BaseScrapyMonitor(Monitor, SpiderMonitorMixin):
    longMessage = False

    def get_settings(self, name, default=None):
        """ Return a settings prioritized by:

            #. ``{name}`` as a spider attribute if is present
            #. ``{name}.upper()`` in the ``crawler.settings`` object
            #. If ``crawler.settings.{name}`` is a dict, try to get the
               ``{spider.name}`` key of that dictionary, this allows you to
               have a different configuration per spider in a settings level,
               like:

               .. code-block:: python

                   SPIDERMON_MAX_ERROR = {
                        'my_spider': 100,
                        'other_spider': 10,
                   }

        """
        settings_value = self.crawler.settings.get(name.upper())
        if type(settings_value) == dict:
            settings_value = settings_value.get(self.spider.name, None)
        spider_value = getattr(self.spider, name.lower(), None)
        return spider_value or settings_value or default


@monitors.name('Extracted Items Monitor')
class ItemCountMonitor(BaseScrapyMonitor):
    """ Check for the minimum number of extracted items.
    You can configure it using ``SPIDERMON_MIN_ITEMS`` setting.
    There's **NO** default value for this setting, if you try to use this
    monitor without setting it it'll raise a ``NotConfigured`` exception
    """

    @monitors.name('Should extract the minimum amount of items')
    def test_minimum_number_of_items(self):
        minimum_threshold = self.get_settings(SPIDERMON_MIN_ITEMS)
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
    """ Check for errors in the spider log you can configure the expected
    number of ERROR log messages using ``SPIDERMON_MAX_ERROR``,
    the default is ``0``."""

    @monitors.name('Should not have any errors')
    def test_should_not_have_errors(self):
        errors_threshold = self.get_settings(SPIDERMON_MAX_ERROR, 0)
        no_of_errors = self.stats.get('log_count/ERROR', 0)
        msg = 'Found {} errors in log, maximum expected is '\
              '{}'.format(no_of_errors, errors_threshold)
        self.assertTrue(no_of_errors <= errors_threshold, msg=msg)


@monitors.name('Finish Reason Monitor')
class FinishReasonMonitor(BaseScrapyMonitor):
    """ Check if a job has a expected finish reason.
    You can configure the expected reason with the
    ``SPIDERMON_EXPECTED_FINISH_REASONS``, it should be an ``iterable`` of
    valid finish reasons.

    The default value of this settings is: ``['finished', ]``"""

    @monitors.name('Should have the expected finished reason(s)')
    def test_should_not_have_errors(self):
        expected_reasons = self.get_settings(
            SPIDERMON_EXPECTED_FINISH_REASONS, ('finished', ))
        finished_reason = self.stats.get('finish_reason')
        msg = 'Finished with "{}" the expected reasons are {}'.format(
                finished_reason, expected_reasons)
        self.assertTrue(finished_reason in expected_reasons, msg=msg)


@monitors.name('Check for unwanted http status codes')
class UnwantedHttpStatus(BaseScrapyMonitor):
    """ Check for maximum number of unwanted http codes.

    You can configure a list of unwanted http codes with
    ``SPIDERMON_UNWANTED_HTTP_CODES`` the default value is:
    ``[400, 407, 429, 500, 502, 503, 504, 523, 540, 541]``

    You can also configured the **maximum** number of times that those
    response codes with ``SPIDERMON_MAX_UNWANTED_HTTP_CODES`` the default
    value is ``1``.
    """
    default_codes = [400, 407, 429, 500, 502, 503, 504, 523, 540, 541]

    @monitors.name('Should not hit the limit of unwanted http status')
    def test_check_unwanted_http_codes(self):
        max_errors = self.get_settings(SPIDERMON_MAX_UNWANTED_HTTP_CODES, 1)
        error_codes = self.get_settings(SPIDERMON_UNWANTED_HTTP_CODES,
                                        self.default_codes)
        for code in error_codes:
            times = self.stats.get(
                f'downloader/response_status_count/{code}', 0)
            msg = f'Found {times} Responses with status code={code} - '\
                  f'This exceed the limit of {max_errors}'
            self.assertTrue(times < max_errors, msg=msg)


class SpiderCloseMonitorSuite(MonitorSuite):
    """ Implemented the following monitors:

    * :class:`ItemCountMonitor`
    * :class:`LogMonitor`
    * :class:`FinishReasonMonitor`
    * :class:`UnwantedHttpStatus`

    You can easily enable this monitor *after* enabling Spidermon::

            SPIDERMON_SPIDER_CLOSE_MONITORS = (
                'spidermon.contrib.scrapy.monitors.SpiderCloseMonitorSuite',
            )

    """
    monitors = [
        ItemCountMonitor,
        LogMonitor,
        FinishReasonMonitor,
        UnwantedHttpStatus,
    ]
