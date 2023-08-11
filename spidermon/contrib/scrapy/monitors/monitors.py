import datetime
import json
import math
import os

from spidermon import Monitor, monitors
from spidermon.exceptions import NotConfigured
from spidermon.utils.zyte import Client
from spidermon.utils.settings import getdictorlist
from spidermon.contrib.monitors.mixins.stats import StatsMonitorMixin

from .base import BaseScrapyMonitor, BaseStatMonitor

SPIDERMON_EXPECTED_FINISH_REASONS = "SPIDERMON_EXPECTED_FINISH_REASONS"
SPIDERMON_UNWANTED_HTTP_CODES = "SPIDERMON_UNWANTED_HTTP_CODES"
SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT = "SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT"
SPIDERMON_MAX_EXECUTION_TIME = "SPIDERMON_MAX_EXECUTION_TIME"
SPIDERMON_MAX_RETRIES = "SPIDERMON_MAX_RETRIES"
SPIDERMON_MIN_SUCCESSFUL_REQUESTS = "SPIDERMON_MIN_SUCCESSFUL_REQUESTS"
SPIDERMON_MAX_REQUESTS_ALLOWED = "SPIDERMON_MAX_REQUESTS_ALLOWED"
SPIDERMON_JOBS_COMPARISON = "SPIDERMON_JOBS_COMPARISON"
SPIDERMON_JOBS_COMPARISON_STATES = "SPIDERMON_JOBS_COMPARISON_STATES"
SPIDERMON_JOBS_COMPARISON_TAGS = "SPIDERMON_JOBS_COMPARISON_TAGS"
SPIDERMON_JOBS_COMPARISON_THRESHOLD = "SPIDERMON_JOBS_COMPARISON_THRESHOLD"
SPIDERMON_ITEM_COUNT_INCREASE = "SPIDERMON_ITEM_COUNT_INCREASE"


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

    Furthermore, instead of being a numeric value, the code accepts a dictionary which can
    contain any of two keys: ``max_count`` and ``max_percentage``. The former refers to an
    absolute value and works the same way as setting an integer value. The latter refers
    to a max_percentage of the total number of requests the spider made. If both are set, the
    monitor will fail if any of the conditions are met. If none are set, it will default to
    ``DEFAULT_UNWANTED_HTTP_CODES_MAX_COUNT```.

    With the following setting, the monitor will fail if it has at least one 500 error or
    if there are more than ``min(100, 0.5 * total requests)`` 400 responses.

    .. highlight:: python
    .. code-block:: python

        SPIDERMON_UNWANTED_HTTP_CODES = {
            400: {"max_count": 100, "max_percentage": 0.5},
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

        requests = self.stats.get("downloader/request_count", 0)
        for code, max_errors in unwanted_http_codes.items():
            code = int(code)
            count = self.stats.get(f"downloader/response_status_count/{code}", 0)

            percentage_trigger = False

            if isinstance(max_errors, dict):
                absolute_max_errors = max_errors.get("max_count")
                percentual_max_errors = max_errors.get("max_percentage")

                # if the user passed an empty dict, use the default count
                if not absolute_max_errors and not percentual_max_errors:
                    max_errors = self.DEFAULT_UNWANTED_HTTP_CODES_MAX_COUNT

                else:
                    # calculate the max errors based on percentage
                    # if there's no percentage set, take the number
                    # of requests as this is the same as disabling the check
                    calculated_percentage_errors = int(
                        percentual_max_errors * requests
                        if percentual_max_errors
                        else requests
                    )

                    # takes the minimum of the two values.
                    # if no absolute max errors were set, take the number
                    # of requests as this effectively disables this check
                    max_errors = min(
                        absolute_max_errors if absolute_max_errors else requests,
                        calculated_percentage_errors,
                    )

                    # if the max errors were defined by the percentage, remember it
                    # so we can properly format the error message.
                    percentage_trigger = max_errors == calculated_percentage_errors

            stat_message = (
                "This exceeds the limit of {} ({}% of {} total requests)".format(
                    max_errors, percentual_max_errors * 100, requests
                )
                if percentage_trigger
                else "This exceeds the limit of {}".format(max_errors)
            )

            msg = (
                "Found {} Responses with status code={} - ".format(count, code)
                + stat_message
            )
            self.assertTrue(count <= max_errors, msg=msg)


@monitors.name("Downloader Exceptions monitor")
class DownloaderExceptionMonitor(BaseStatMonitor):
    """This monitor checks if the amount of downloader
    exceptions (timeouts, rejected connections, etc.) is
    lesser or equal to a specified threshold.

    This amount is provided by ``downloader/exception_count``
    value of your job statistics. If the value is not available
    in the statistics (i.e., no exception was raised), the monitor
    will be skipped.

    Configure the threshold using the ``SPIDERMON_MAX_DOWNLOADER_EXCEPTIONS``
    setting. There's **NO** default value for this setting.
    If you try to use this monitor without a value specified, a
    ``NotConfigured`` exception will be raised.
    """

    stat_name = "downloader/exception_count"
    threshold_setting = "SPIDERMON_MAX_DOWNLOADER_EXCEPTIONS"
    assert_type = "<="
    fail_if_stat_missing = False


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
class ItemValidationMonitor(BaseStatMonitor):
    """This monitor checks if the amount of validation errors
    is lesser or equal to a specified threshold.

    This amount is provided by ``spidermon/validation/fields/errors``
    value of your job statistics. If the value is not available
    in the statistics (i.e., no validation errors), the monitor
    will be skipped.

    .. warning::

       You need to enable item validation in your project so
       this monitor can be used.

    Configure the threshold using the ``SPIDERMON_MAX_ITEM_VALIDATION_ERRORS``
    setting. There's **NO** default value for this setting.
    If you try to use this monitor without a value specified, a
    ``NotConfigured`` exception will be raised.
    """

    stat_name = "spidermon/validation/fields/errors"
    threshold_setting = "SPIDERMON_MAX_ITEM_VALIDATION_ERRORS"
    assert_type = "<="
    fail_if_stat_missing = False


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

    If a field returned by your spider is a list of dicts (or objects) and you want to check their
    coverage, that is also possible. You need to set the ``SPIDERMON_LIST_FIELDS_COVERAGE_LEVELS``
    setting. This value represents for how many levels inside the list the coverage will be computed
    (if the objects inside the list also have fields that are objects/lists).
    The coverage for list fields is computed in two ways: with
    respect to the total items scraped (these values can be greater than 1) and with respect to the
    total of items in the list. The stats are in the following form:

    .. code-block:: python

        {
            "spidermon_field_coverage/dict/field2/_items/nested_field1": "some_value",
            "spidermon_field_coverage/dict/field2/nested_field1": "other_value",
        }

    The stat containing `_items` means it is calculated based on the total list items, while the
    other, based on the total number of scraped items.

    If the objects in the list also contain another list field, that coverage is also computed in
    both ways, with the total list items considered for the `_items` stat that of the innermost list.

    In case you have a job without items scraped, and you want to skip this test, you have to enable the
    ``SPIDERMON_FIELD_COVERAGE_SKIP_IF_NO_ITEM`` setting to avoid the field coverage monitor error.

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
           }

    """

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
        skip_no_items = self.crawler.settings.getbool(
            "SPIDERMON_FIELD_COVERAGE_SKIP_IF_NO_ITEM", False
        )
        items_scraped = self.data.stats.get("item_scraped_count", 0)
        if skip_no_items and int(items_scraped) == 0:
            self.skipTest("No items were scraped.")

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


@monitors.name("Periodic execution time monitor")
class PeriodicExecutionTimeMonitor(Monitor, StatsMonitorMixin):
    """Check for runtime exceeding a target maximum runtime.

    You can configure the maximum runtime (in seconds) using
    ``SPIDERMON_MAX_EXECUTION_TIME`` as a project setting or spider attribute."""

    @monitors.name("Maximum execution time reached")
    def test_execution_time(self):
        crawler = self.data.get("crawler")
        max_execution_time = crawler.settings.getint(SPIDERMON_MAX_EXECUTION_TIME)
        if not max_execution_time:
            return
        now = datetime.datetime.utcnow()
        start_time = self.data.stats.get("start_time")
        if not start_time:
            return

        duration = now - start_time

        msg = "The job has exceeded the maximum execution time"
        self.assertLess(duration.total_seconds(), max_execution_time, msg=msg)


@monitors.name("Jobs Comparison Monitor")
class ZyteJobsComparisonMonitor(BaseStatMonitor):
    """
    .. note::
       This monitor is useful when running jobs in
       `Zyte's Scrapy Cloud <https://www.zyte.com/scrapy-cloud/>`_.

    Check for a drop in scraped item count compared to previous jobs.

    You need to set the number of previous jobs to compare, using ``SPIDERMON_JOBS_COMPARISON``.
    The default is ``0`` which disables the monitor. We use the average of the scraped items count.

    You can configure which percentage of the previous item count is the minimum acceptable, by
    using the setting ``SPIDERMON_JOBS_COMPARISON_THRESHOLD``. We expect a float number between
    ``0.0`` (not inclusive) and with no upper limit (meaning we can check if itemcount is increasing
    at a certain rate). If not set, a NotConfigured error will be raised.

    You can filter which jobs to compare based on their states using the
    ``SPIDERMON_JOBS_COMPARISON_STATES`` setting. The default value is ``("finished",)``.

    You can also filter which jobs to compare based on their tags using the
    ``SPIDERMON_JOBS_COMPARISON_TAGS`` setting. Among the defined tags we consider only those
    that are also present in the current job.
    """

    stat_name = "item_scraped_count"
    assert_type = ">="

    def run(self, result):
        if (
            SPIDERMON_JOBS_COMPARISON not in self.crawler.settings.attributes
            or self.crawler.settings.getint(SPIDERMON_JOBS_COMPARISON) <= 0
        ):
            raise NotConfigured(
                f"Configure SPIDERMON_JOBS_COMPARISON to your project "
                f"settings to use {self.monitor_name}."
            )

        if (
            SPIDERMON_JOBS_COMPARISON_THRESHOLD not in self.crawler.settings.attributes
            or self.crawler.settings.getfloat(SPIDERMON_JOBS_COMPARISON_THRESHOLD) <= 0
        ):
            raise NotConfigured(
                f"Configure SPIDERMON_JOBS_COMPARISON_THRESHOLD to your project "
                f"settings to use {self.monitor_name}."
            )

        return super().run(result)

    def _get_jobs(self, states, number_of_jobs):
        tags = self._get_tags_to_filter()

        jobs = []
        start = 0
        client = Client(self.crawler.settings)

        _jobs = client.spider.jobs.list(
            start=start,
            state=states,
            count=number_of_jobs,
            filters=dict(has_tag=tags) if tags else None,
        )
        while _jobs:
            jobs.extend(_jobs)
            start += 1000
            _jobs = client.spider.jobs.list(
                start=start,
                state=states,
                count=number_of_jobs,
                filters=dict(has_tag=tags) if tags else None,
            )
        return jobs

    def _get_tags_to_filter(self):
        """
        Return the intersect of the desired tags to filter and
        the ones from the current job.
        """
        desired_tags = self.crawler.settings.getlist(SPIDERMON_JOBS_COMPARISON_TAGS)
        if not desired_tags:
            return {}

        current_tags = json.loads(os.environ.get("SHUB_JOB_DATA", "{}")).get("tags")
        if not current_tags:
            return {}

        tags_to_filter = set(desired_tags) & set(current_tags)
        return sorted(tags_to_filter)

    def get_threshold(self):
        number_of_jobs = self.crawler.settings.getint(SPIDERMON_JOBS_COMPARISON)

        threshold = self.crawler.settings.getfloat(SPIDERMON_JOBS_COMPARISON_THRESHOLD)

        states = self.crawler.settings.getlist(
            SPIDERMON_JOBS_COMPARISON_STATES, ("finished",)
        )

        jobs = self._get_jobs(states, number_of_jobs)

        previous_count = sum(job.get("items", 0) for job in jobs) / len(jobs)

        expected_item_extracted = math.ceil(previous_count * threshold)
        return expected_item_extracted


@monitors.name("Periodic Item Count Increase Monitor")
class PeriodicItemCountMonitor(BaseStatMonitor):
    """Check for increase in item count.

    You can configure the threshold for increase using
    ``SPIDERMON_ITEM_COUNT_INCREASE`` as a project setting or spider attribute.
    Use int value to check for x new items every check or float value to check
    in percentage increase of items.
    """

    stat_name = "item_scraped_count"
    threshold_setting = "SPIDERMON_ITEM_COUNT_INCREASE"
    assert_type = ">="

    def run(self, result):
        if SPIDERMON_ITEM_COUNT_INCREASE not in self.crawler.settings.attributes:
            raise NotConfigured(
                f"Configure {SPIDERMON_ITEM_COUNT_INCREASE} to your project "
                f"settings to use {self.monitor_name}."
            )

        return super().run(result)

    def get_threshold(self):
        crawler = self.data.crawler
        prev_item_scraped_count = self.stats.get("prev_item_scraped_count", 0)
        item_scraped_count = self.stats.get(self.stat_name)
        crawler.stats.set_value("prev_item_scraped_count", item_scraped_count)
        threshold_increase = crawler.settings.get(self.threshold_setting)
        if isinstance(threshold_increase, int):
            return prev_item_scraped_count + threshold_increase
        elif isinstance(threshold_increase, float):
            return prev_item_scraped_count + (
                prev_item_scraped_count * threshold_increase
            )
