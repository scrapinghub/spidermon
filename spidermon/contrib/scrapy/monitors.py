from spidermon import Monitor, MonitorSuite, monitors
from spidermon.exceptions import NotConfigured
from spidermon.utils.settings import getdictorlist

from ..monitors.mixins.spider import SpiderMonitorMixin

SPIDERMON_EXPECTED_FINISH_REASONS = "SPIDERMON_EXPECTED_FINISH_REASONS"
SPIDERMON_UNWANTED_HTTP_CODES = "SPIDERMON_UNWANTED_HTTP_CODES"
SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT = "SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT"
SPIDERMON_MAX_ITEM_VALIDATION_ERRORS = "SPIDERMON_MAX_ITEM_VALIDATION_ERRORS"
SPIDERMON_MAX_RETRIES = "SPIDERMON_MAX_RETRIES"
SPIDERMON_MAX_DOWNLOADER_EXCEPTIONS = "SPIDERMON_MAX_DOWNLOADER_EXCEPTIONS"
SPIDERMON_MIN_SUCCESSFUL_REQUESTS = "SPIDERMON_MIN_SUCCESSFUL_REQUESTS"
SPIDERMON_MAX_REQUESTS_ALLOWED = "SPIDERMON_MAX_REQUESTS_ALLOWED"


class BaseScrapyMonitor(Monitor, SpiderMonitorMixin):
    longMessage = False

    @property
    def monitor_description(self):
        if self.__class__.__doc__:
            return self.__class__.__doc__.split("\n")[0]
        return super().monitor_description


class BaseStatMonitor(BaseScrapyMonitor):
    """Base Monitor class for stat-related monitors.

    Create a monitor class inheriting from this class to have a custom
    monitor that validates numerical stats from your job execution
    against a configurable threshold.

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
                f"Configure {self.threshold_setting} to your project"
                f"settings to use {self.monitor_name}."
            )

        return super().run(result)

    def _get_threshold_value(self):
        if hasattr(self, "get_threshold"):
            return self.get_threshold()
        return self.crawler.settings.get(self.threshold_setting)

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


@monitors.name("Extracted Items Monitor")
class ItemCountMonitor(BaseStatMonitor):
    """Check if spider extracted the minimum number of items.

    You can configure it using ``SPIDERMON_MIN_ITEMS`` setting.
    There's **NO** default value for this setting, if you try to use this
    monitor without setting it, it'll raise a ``NotConfigured`` exception.
    """

    stat_name = "item_scraped_count"
    threshold_setting = "SPIDERMON_MIN_ITEMS"
    assert_type = ">="


@monitors.name("Critical Count Monitor")
class CriticalCountMonitor(BaseStatMonitor):
    """Check for critical errors in the spider log.

    You can configure it using ``SPIDERMON_MAX_CRITICALS`` setting.
    There's **NO** default value for this setting, if you try to use this
    monitor without setting it, it'll raise a ``NotConfigured`` exception.

    If the job doesn't have any critical error, the monitor will be skipped."""

    stat_name = "log_count/CRITICAL"
    threshold_setting = "SPIDERMON_MAX_CRITICALS"
    assert_type = "<="
    fail_if_stat_missing = False


@monitors.name("Error Count Monitor")
class ErrorCountMonitor(BaseStatMonitor):
    """Check for errors in the spider log.

    You can configure it using ``SPIDERMON_MAX_ERRORS`` setting.
    There's **NO** default value for this setting, if you try to use this
    monitor without setting it, it'll raise a ``NotConfigured`` exception.

    If the job doesn't have any error, the monitor will be skipped."""

    stat_name = "log_count/ERROR"
    threshold_setting = "SPIDERMON_MAX_ERRORS"
    assert_type = "<="
    fail_if_stat_missing = False


@monitors.name("Warning Count Monitor")
class WarningCountMonitor(BaseStatMonitor):
    """Check for warnings in the spider log.

    You can configure it using ``SPIDERMON_MAX_WARNINGS`` setting.
    There's **NO** default value for this setting, if you try to use this
    monitor without setting it, it'll raise a ``NotConfigured`` exception.

    If the job doesn't have any warning, the monitor will be skipped."""

    stat_name = "log_count/WARNING"
    threshold_setting = "SPIDERMON_MAX_WARNINGS"
    assert_type = "<="
    fail_if_stat_missing = False


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
