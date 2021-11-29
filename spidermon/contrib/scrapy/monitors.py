from spidermon import Monitor, MonitorSuite, monitors
from spidermon.exceptions import NotConfigured
from spidermon.utils.settings import getdictorlist

from ..monitors.mixins.spider import SpiderMonitorMixin

SPIDERMON_MIN_ITEMS = "SPIDERMON_MIN_ITEMS"
SPIDERMON_MAX_ERRORS = "SPIDERMON_MAX_ERRORS"
SPIDERMON_MAX_WARNINGS = "SPIDERMON_MAX_WARNINGS"
SPIDERMON_EXPECTED_FINISH_REASONS = "SPIDERMON_EXPECTED_FINISH_REASONS"
SPIDERMON_UNWANTED_HTTP_CODES = "SPIDERMON_UNWANTED_HTTP_CODES"
SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT = "SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT"
SPIDERMON_MAX_ITEM_VALIDATION_ERRORS = "SPIDERMON_MAX_ITEM_VALIDATION_ERRORS"
SPIDERMON_MAX_RETRIES = "SPIDERMON_MAX_RETRIES"
SPIDERMON_MAX_DOWNLOADER_EXCEPTIONS = "SPIDERMON_MAX_DOWNLOADER_EXCEPTIONS"
SPIDERMON_MIN_SUCCESSFUL_REQUESTS = "SPIDERMON_MIN_SUCCESSFUL_REQUESTS"
SPIDERMON_MAX_REQUESTS_ALLOWED = "SPIDERMON_MAX_REQUESTS_ALLOWED"
SPIDERMON_JOBS_COMPARISON = "SPIDERMON_JOBS_COMPARISON"
SPIDERMON_JOBS_COMPARISON_STATUS = "SPIDERMON_JOBS_COMPARISON_STATUS"
SPIDERMON_JOBS_COMPARISON_THRESHOLD = "SPIDERMON_JOBS_COMPARISON_THRESHOLD"


class BaseScrapyMonitor(Monitor, SpiderMonitorMixin):
    longMessage = False

    @property
    def monitor_description(self):
        if self.__class__.__doc__:
            return self.__class__.__doc__.split("\n")[0]
        return super().monitor_description


@monitors.name("Extracted Items Monitor")
class ItemCountMonitor(BaseScrapyMonitor):
    """Check if spider extracted the minimum number of items.

    You can configure it using ``SPIDERMON_MIN_ITEMS`` setting.
    There's **NO** default value for this setting, if you try to use this
    monitor without setting it, it'll raise a ``NotConfigured`` exception.
    """

    def run(self, result):
        self.minimum_threshold = self.crawler.settings.getint(SPIDERMON_MIN_ITEMS, 0)
        if not self.minimum_threshold:
            raise NotConfigured(
                "You should specify a minimum number of items " "to check against."
            )
        return super().run(result)

    @monitors.name("Should extract the minimum amount of items")
    def test_minimum_number_of_items(self):
        item_extracted = getattr(self.stats, "item_scraped_count", 0)
        msg = "Extracted {} items, the expected minimum is {}".format(
            item_extracted, self.minimum_threshold
        )
        self.assertTrue(item_extracted >= self.minimum_threshold, msg=msg)


@monitors.name("Error Count Monitor")
class ErrorCountMonitor(BaseScrapyMonitor):
    """Check for errors in the spider log.

    You can configure the expected number of ERROR log messages using
    ``SPIDERMON_MAX_ERRORS``. The default is ``0``."""

    @monitors.name("Should not have any errors")
    def test_max_errors_in_log(self):
        errors_threshold = self.crawler.settings.getint(SPIDERMON_MAX_ERRORS, 0)
        no_of_errors = self.stats.get("log_count/ERROR", 0)
        msg = "Found {} errors in log, maximum expected is " "{}".format(
            no_of_errors, errors_threshold
        )
        self.assertTrue(no_of_errors <= errors_threshold, msg=msg)


@monitors.name("Warning Count Monitor")
class WarningCountMonitor(BaseScrapyMonitor):
    """Check for warnings in the spider log.

    You can configure the expected number of WARNINGS log messages using
    ``SPIDERMON_MAX_WARNINGS``. The default is ``-1`` which disables the monitor."""

    @monitors.name("Should not have any warnings")
    def test_max_errors_in_log(self):
        warnings_threshold = self.crawler.settings.getint(SPIDERMON_MAX_WARNINGS, -1)
        if warnings_threshold < 0:
            return
        no_of_warnings = self.stats.get("log_count/WARNING", 0)
        msg = "Found {} warnings in log, maximum expected is " "{}".format(
            no_of_warnings, warnings_threshold
        )
        self.assertTrue(no_of_warnings <= warnings_threshold, msg=msg)


@monitors.name("Finish Reason Monitor")
class FinishReasonMonitor(BaseScrapyMonitor):
    """Check if a job has a expected finish reason.

    You can configure the expected reason with the
    ``SPIDERMON_EXPECTED_FINISH_REASONS``, it should be an ``iterable`` of
    valid finish reasons.

    The default value of this settings is: ``['finished', ]``."""

    @monitors.name("Should have the expected finished reason(s)")
    def test_should_finish_with_expected_reason(self):
        expected_reasons = self.crawler.settings.getlist(
            SPIDERMON_EXPECTED_FINISH_REASONS, ("finished",)
        )
        finished_reason = self.stats.get("finish_reason")
        msg = 'Finished with "{}" the expected reasons are {}'.format(
            finished_reason, expected_reasons
        )
        self.assertTrue(finished_reason in expected_reasons, msg=msg)


@monitors.name("Unwanted HTTP codes monitor")
class UnwantedHTTPCodesMonitor(BaseScrapyMonitor):
    """Check for maximum number of unwanted HTTP codes.
    You can configure it using ``SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT`` setting
    or ``SPIDERMON_UNWANTED_HTTP_CODES`` setting

    This monitor fails if during the spider execution, we receive
    more than the number of ``SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT``
    setting for at least one of the HTTP Status Codes in the list defined in
    ``SPIDERMON_UNWANTED_HTTP_CODES`` setting.

    Default values are:

    .. highlight:: python
    .. code-block:: python

        SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT = 10
        SPIDERMON_UNWANTED_HTTP_CODES = [400, 407, 429, 500, 502, 503, 504, 523, 540, 541]

    ``SPIDERMON_UNWANTED_HTTP_CODES`` can also be a dictionary with the HTTP Status Code
    as key and the maximum number of accepted responses with that code.

    With the following setting, the monitor will fail if more than 100 responses are
    404 errors or at least one 500 error:

    .. highlight:: python
    .. code-block:: python

        SPIDERMON_UNWANTED_HTTP_CODES = {
            400: 100,
            500: 0,
        }

    """

    DEFAULT_UNWANTED_HTTP_CODES_MAX_COUNT = 10
    DEFAULT_UNWANTED_HTTP_CODES = [400, 407, 429, 500, 502, 503, 504, 523, 540, 541]

    @monitors.name("Should not hit the limit of unwanted http status")
    def test_check_unwanted_http_codes(self):
        unwanted_http_codes = getdictorlist(
            self.crawler,
            SPIDERMON_UNWANTED_HTTP_CODES,
            self.DEFAULT_UNWANTED_HTTP_CODES,
        )

        errors_max_count = self.crawler.settings.getint(
            SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT,
            self.DEFAULT_UNWANTED_HTTP_CODES_MAX_COUNT,
        )

        if not isinstance(unwanted_http_codes, dict):
            unwanted_http_codes = {
                code: errors_max_count for code in unwanted_http_codes
            }

        for code, max_errors in unwanted_http_codes.items():
            code = int(code)
            count = self.stats.get(f"downloader/response_status_count/{code}", 0)
            msg = (
                "Found {} Responses with status code={} - "
                "This exceed the limit of {}".format(count, code, max_errors)
            )
            self.assertTrue(count <= max_errors, msg=msg)


@monitors.name("Downloader Exceptions monitor")
class DownloaderExceptionMonitor(BaseScrapyMonitor):
    """Check the amount of downloader exceptions (timeouts, rejected
    connections, etc.).

    You can configure it using the ``SPIDERMON_MAX_DOWNLOADER_EXCEPTIONS`` setting.
    The default is ``-1`` which disables the monitor.
    """

    @monitors.name("Should not hit the limit of downloader exceptions")
    def test_maximum_downloader_exceptions(self):
        exception_count = self.stats.get("downloader/exception_count", 0)
        threshold = self.crawler.settings.getint(
            SPIDERMON_MAX_DOWNLOADER_EXCEPTIONS, -1
        )
        if threshold < 0:
            return
        msg = "Too many downloader exceptions ({})".format(exception_count)
        self.assertLessEqual(exception_count, threshold, msg=msg)


@monitors.name("Retry Count monitor")
class RetryCountMonitor(BaseScrapyMonitor):
    """Check if any requests have reached the maximum amount of retries
    and the crawler had to drop those requests.

    You can configure it using the ``SPIDERMON_MAX_RETRIES`` setting.
    The default is ``-1`` which disables the monitor.
    """

    @monitors.name(
        "Should not hit the limit of requests that reached the maximum retry amount"
    )
    def test_maximum_retries(self):
        max_reached = self.stats.get("retry/max_reached", 0)
        threshold = self.crawler.settings.getint(SPIDERMON_MAX_RETRIES, -1)
        if threshold < 0:
            return
        msg = "Too many requests ({}) reached the maximum retry amount".format(
            max_reached
        )
        self.assertLessEqual(max_reached, threshold, msg=msg)


@monitors.name("Successful Requests monitor")
class SuccessfulRequestsMonitor(BaseScrapyMonitor):
    """Check the amount of successful requests.

    You can configure it using the ``SPIDERMON_MIN_SUCCESSFUL_REQUESTS`` setting.
    """

    @monitors.name("Should have at least the minimum number of successful requests")
    def test_minimum_successful_requests(self):
        requests = self.stats.get("downloader/response_status_count/200", 0)
        threshold = self.crawler.settings.getint(SPIDERMON_MIN_SUCCESSFUL_REQUESTS, 0)
        msg = "Too few ({}) successful requests".format(requests)
        self.assertGreaterEqual(requests, threshold, msg=msg)


@monitors.name("Total Requests monitor")
class TotalRequestsMonitor(BaseScrapyMonitor):
    """Check the total amount of requests.

    You can configure it using the ``SPIDERMON_MAX_REQUESTS_ALLOWED`` setting.
    The default is ``-1`` which disables the monitor.
    """

    @monitors.name("Should not hit the total limit of requests")
    def test_request_count_exceeded_limit(self):
        requests = self.stats.get("downloader/request_count", 0)
        threshold = self.crawler.settings.getint(SPIDERMON_MAX_REQUESTS_ALLOWED, -1)
        if threshold < 0:
            return
        msg = "Too many ({}) requests".format(requests)
        self.assertLessEqual(requests, threshold, msg=msg)


@monitors.name("Item Validation Monitor")
class ItemValidationMonitor(BaseScrapyMonitor):
    """Check for item validation errors if item validation pipelines are enabled.

    You can configure the maximum number of item validation errors using
    ``SPIDERMON_MAX_ITEM_VALIDATION_ERRORS``. The default is ``0``."""

    @monitors.name("Should not have more item validation errors than configured.")
    def test_verify_item_validation_error(self):
        errors_threshold = self.crawler.settings.getint(
            SPIDERMON_MAX_ITEM_VALIDATION_ERRORS, 0
        )
        item_validation_errors = self.stats.get("spidermon/validation/fields/errors", 0)
        msg = "Found {} item validation error. Max allowed is {}.".format(
            item_validation_errors, errors_threshold
        )
        self.assertTrue(item_validation_errors <= errors_threshold, msg=msg)


@monitors.name("Field Coverage Monitor")
class FieldCoverageMonitor(BaseScrapyMonitor):
    """Validate if field coverage rules are met.

    To use this monitor you need to enable the ``SPIDERMON_ADD_FIELD_COVERAGE``
    setting, which will add information about field coverage to your spider
    statistics.

    To define your field coverage rules create a dictionary containing the
    expected coverage for each field you want to monitor.

    As an example, if the items you are returning from your spider are Python dictionaries
    with the following format:

    .. code-block:: python

        {
            "field_1": "some_value",
            "field_2": "some_value",
            "field_3": {
                "field_3_1": "some_value",
                "field_3_2": "some_value",
            }
        }

    A set of rules may be defined as follows:

    .. code-block:: python

        # project/settings.py
        SPIDERMON_FIELD_COVERAGE_RULES = {
            "dict/field_1": 0.4,  # Expected 40% coverage for field_1
            "dict/field_2": 1.0,  # Expected 100% coverage for field_2
            "dict/field_3": 0.8,  # Expected 80% coverage for parent field_3
            "dict/field_3/field_3_1": 0.5,  # Expected 50% coverage for nested field_3_1
        }

    You are not obligated to set rules for every field, just for the ones in which you are interested.
    Also, you can monitor nested fields if available in your returned items.

    .. warning::

       Rules for nested fields will be validated against the total number of items returned.

       For the example below, rule for ``dict/field_3/field_3_1`` will validate if 50%
       of **all** items returned contains ``field_3_1``, not just the ones that contain
       parent ``field_3``.

    .. note::
       If you are returning an item type other than a dictionary, replace `dict` by the
       class name of the item you are returning.

       Considering you have an item defined as:

       .. code-block:: python

           class MyCustomItem(scrapy.Item):
               field_1 = scrapy.Field()
               field_2 = scrapy.Field()

       You must define the field coverage rules as follows:

       .. code-block:: python

           SPIDERMON_FIELD_COVERAGE_RULES = {
               "MyCustomItem/field_1": 0.4,
               "MyCustomItem/field_2": 1.0,
           }"""

    def run(self, result):
        add_field_coverage_set = self.crawler.settings.getbool(
            "SPIDERMON_ADD_FIELD_COVERAGE", False
        )
        if not add_field_coverage_set:
            raise NotConfigured(
                "To enable field coverage monitor, set SPIDERMON_ADD_FIELD_COVERAGE=True in your project settings"
            )
        return super().run(result)

    def test_check_if_field_coverage_rules_are_met(self):
        failures = []
        field_coverage_rules = self.crawler.settings.getdict(
            "SPIDERMON_FIELD_COVERAGE_RULES"
        )
        for field, expected_coverage in field_coverage_rules.items():
            actual_coverage = self.data.stats.get(
                f"spidermon_field_coverage/{field}", 0
            )
            if actual_coverage < expected_coverage:
                failures.append(
                    "{} (expected {}, got {})".format(
                        field, expected_coverage, actual_coverage
                    )
                )

        msg = "\nThe following items did not meet field coverage rules:\n{}".format(
            "\n".join(failures)
        )
        self.assertTrue(len(failures) == 0, msg=msg)


@monitors.name("Jobs Comparison Monitor")
class JobsComparisonMonitor(BaseScrapyMonitor):
    """Check for a drop in scraped item count compared to previous jobs.

    You need to set the number of previous jobs to compare, using ``SPIDERMON_JOBS_COMPARISON``.
    The default is ``0`` which disables the monitor. We use the average of the scraped items count.

    You can configure which percentage of the previous item count is the minimum acceptable, by
    using the setting ``SPIDERMON_JOBS_COMPARISON_THRESHOLD``. We expect a float number between
    ``0.0`` and ``1.0``. The default is ``0.8``.

    You can filter which jobs to compare based on their status using the
    ``SPIDERMON_JOBS_COMPARISON_STATUS`` setting. The default is ``("finished",)``.
    """

    @monitors.name("Should not have a big drop in item count compared to previous jobs")
    def test_if_item_count_from_previous_jobs_have_decreased(self):
        # 1. get the number of jobs and check if monitor is enabled
        number_of_jobs = self.crawler.settings.getint(SPIDERMON_JOBS_COMPARISON, 0)
        if not number_of_jobs:
            return

        assert False


class SpiderCloseMonitorSuite(MonitorSuite):
    """This Monitor Suite implements the following monitors:

    * :class:`ItemCountMonitor`
    * :class:`ItemValidationMonitor`
    * :class:`ErrorCountMonitor`
    * :class:`WarningCountMonitor`
    * :class:`FinishReasonMonitor`
    * :class:`UnwantedHTTPCodesMonitor`
    * :class:`FieldCoverageMonitor`
    * :class:`RetryCountMonitor`
    * :class:`DownloaderExceptionMonitor`
    * :class:`SuccessfulRequestsMonitor`
    * :class:`TotalRequestsMonitor`

    You can easily enable this monitor *after* enabling Spidermon::

            SPIDERMON_SPIDER_CLOSE_MONITORS = (
                'spidermon.contrib.scrapy.monitors.SpiderCloseMonitorSuite',
            )
    """

    monitors = [
        ItemCountMonitor,
        ItemValidationMonitor,
        ErrorCountMonitor,
        WarningCountMonitor,
        FinishReasonMonitor,
        UnwantedHTTPCodesMonitor,
        FieldCoverageMonitor,
        RetryCountMonitor,
        DownloaderExceptionMonitor,
        SuccessfulRequestsMonitor,
        TotalRequestsMonitor,
    ]
