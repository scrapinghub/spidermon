from spidermon import MonitorSuite

from .monitors import (
    DownloaderExceptionMonitor,
    ErrorCountMonitor,
    FieldCoverageMonitor,
    FinishReasonMonitor,
    ItemCountMonitor,
    ItemValidationMonitor,
    PeriodicExecutionTimeMonitor,
    RetryCountMonitor,
    SuccessfulRequestsMonitor,
    TotalRequestsMonitor,
    UnwantedHTTPCodesMonitor,
    WarningCountMonitor,
)


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


class PeriodicMonitorSuite(MonitorSuite):
    """This Monitor Suite implements the following monitors:

    * :class:`PeriodicExecutionTimeMonitor`

    You can easily enable this monitor *after* enabling Spidermon::

            SPIDERMON_PERIODIC_MONITORS = {
                'spidermon.contrib.scrapy.monitors.PeriodicMonitorSuite': # check time in seconds,
            }
    """

    monitors = [PeriodicExecutionTimeMonitor]
