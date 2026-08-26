import warnings

from .base import BaseScrapyMonitor, BaseStatMonitor
from .monitors import (
    SPIDERMON_EXPECTED_FINISH_REASONS,
    SPIDERMON_ITEM_COUNT_INCREASE,
    SPIDERMON_MAX_EXECUTION_TIME,
    SPIDERMON_MAX_REQUESTS_ALLOWED,
    SPIDERMON_MAX_RETRIES,
    SPIDERMON_MIN_SUCCESSFUL_REQUESTS,
    SPIDERMON_UNWANTED_HTTP_CODES,
    SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT,
    CriticalCountMonitor,
    DownloaderExceptionMonitor,
    ErrorCountMonitor,
    FieldCoverageMonitor,
    FinishReasonMonitor,
    ItemCountMonitor,
    ItemValidationMonitor,
    PeriodicExecutionTimeMonitor,
    PeriodicItemCountMonitor,
    RetryCountMonitor,
    SuccessfulRequestsMonitor,
    TotalRequestsMonitor,
    UnwantedHTTPCodesMonitor,
    WarningCountMonitor,
)
from .suites import (
    PeriodicItemCountMonitorSuite,
    PeriodicMonitorSuite,
    SpiderCloseMonitorSuite,
)

__all__ = [
    "SPIDERMON_EXPECTED_FINISH_REASONS",
    "SPIDERMON_ITEM_COUNT_INCREASE",
    "SPIDERMON_JOBS_COMPARISON",
    "SPIDERMON_JOBS_COMPARISON_ARGUMENTS",
    "SPIDERMON_JOBS_COMPARISON_CLOSE_REASONS",
    "SPIDERMON_JOBS_COMPARISON_STATES",
    "SPIDERMON_JOBS_COMPARISON_TAGS",
    "SPIDERMON_JOBS_COMPARISON_THRESHOLD",
    "SPIDERMON_MAX_EXECUTION_TIME",
    "SPIDERMON_MAX_REQUESTS_ALLOWED",
    "SPIDERMON_MAX_RETRIES",
    "SPIDERMON_MIN_SUCCESSFUL_REQUESTS",
    "SPIDERMON_UNWANTED_HTTP_CODES",
    "SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT",
    "BaseScrapyMonitor",
    "BaseStatMonitor",
    "CriticalCountMonitor",
    "DownloaderExceptionMonitor",
    "ErrorCountMonitor",
    "FieldCoverageMonitor",
    "FinishReasonMonitor",
    "ItemCountMonitor",
    "ItemValidationMonitor",
    "PeriodicExecutionTimeMonitor",
    "PeriodicItemCountMonitor",
    "PeriodicItemCountMonitorSuite",
    "PeriodicMonitorSuite",
    "RetryCountMonitor",
    "SpiderCloseMonitorSuite",
    "SuccessfulRequestsMonitor",
    "TotalRequestsMonitor",
    "UnwantedHTTPCodesMonitor",
    "WarningCountMonitor",
    "ZyteJobsComparisonMonitor",
]

_ZYTE_NAMES = frozenset(
    {
        "SPIDERMON_JOBS_COMPARISON",
        "SPIDERMON_JOBS_COMPARISON_ARGUMENTS",
        "SPIDERMON_JOBS_COMPARISON_ARGUMENTS_ENABLED",
        "SPIDERMON_JOBS_COMPARISON_CLOSE_REASONS",
        "SPIDERMON_JOBS_COMPARISON_STATES",
        "SPIDERMON_JOBS_COMPARISON_TAGS",
        "SPIDERMON_JOBS_COMPARISON_THRESHOLD",
        "ZyteJobsComparisonMonitor",
    },
)


def __getattr__(name):
    if name in _ZYTE_NAMES:
        from spidermon.contrib.zyte import monitors as zyte_monitors  # noqa: PLC0415

        warnings.warn(
            f"spidermon.contrib.scrapy.monitors.{name} is deprecated, "
            f"import it from spidermon.contrib.zyte.monitors instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(zyte_monitors, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
