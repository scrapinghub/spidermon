from __future__ import absolute_import

from spidermon.contrib.stats.analyzer import StatsAnalyzer
from spidermon.contrib.stats.counters import DictPercentCounter, PercentCounter
from spidermon.exceptions import NotConfigured

from .job import JobMonitorMixin
from .stats import StatsMonitorMixin

DOWNLOADER_RESPONSE_COUNT = "downloader/response_count"
DOWNLOADER_RESPONSE_STATUS = "downloader/response_status_count/"
DOWNLOADER_STATUS_CODES_INFORMATIONAL = [r"1\d{2}$"]
DOWNLOADER_STATUS_CODES_SUCCESSFUL = [r"2\d{2}$"]
DOWNLOADER_STATUS_CODES_REDIRECTIONS = [r"3\d{2}$"]
DOWNLOADER_STATUS_CODES_BAD_REQUESTS = [r"4\d{2}$"]
DOWNLOADER_STATUS_CODES_INTERNAL_SERVER_ERRORS = [r"5\d{2}$"]
DOWNLOADER_STATUS_CODES_OTHERS = ["[^1-5].*$"]
DOWNLOADER_STATUS_CODES_ERRORS = (
    DOWNLOADER_STATUS_CODES_BAD_REQUESTS
    + DOWNLOADER_STATUS_CODES_INTERNAL_SERVER_ERRORS
)


class ResponsesInfo(object):
    def __init__(self, stats):
        self._stats_analyzer = StatsAnalyzer(stats=stats)
        self.count = self._stats_analyzer.search(DOWNLOADER_RESPONSE_COUNT + "$").get(
            DOWNLOADER_RESPONSE_COUNT, 0
        )

        # all status codes
        self.all = DictPercentCounter(total=self.count)
        self._add_status_codes(pattern=None, target=self.all)

        # 1xx. informational
        self.informational = DictPercentCounter(total=self.count)
        self._add_status_codes(
            pattern=DOWNLOADER_STATUS_CODES_INFORMATIONAL, target=self.informational
        )

        # 2xx. successful
        self.successful = DictPercentCounter(total=self.count)
        self._add_status_codes(
            pattern=DOWNLOADER_STATUS_CODES_SUCCESSFUL, target=self.successful
        )

        # 3xx. redirections
        self.redirections = DictPercentCounter(total=self.count)
        self._add_status_codes(
            pattern=DOWNLOADER_STATUS_CODES_REDIRECTIONS, target=self.redirections
        )

        # 4xx. bad requests
        self.bad_requests = DictPercentCounter(total=self.count)
        self._add_status_codes(
            pattern=DOWNLOADER_STATUS_CODES_BAD_REQUESTS, target=self.bad_requests
        )

        # 5xx. internal server errors
        self.internal_server_errors = DictPercentCounter(total=self.count)
        self._add_status_codes(
            pattern=DOWNLOADER_STATUS_CODES_INTERNAL_SERVER_ERRORS,
            target=self.internal_server_errors,
        )

        # >= 6xx. others
        self.others = DictPercentCounter(total=self.count)
        self._add_status_codes(
            pattern=DOWNLOADER_STATUS_CODES_OTHERS, target=self.others
        )

        # errors (4xx + 5xx)
        self.errors = DictPercentCounter(total=self.count)
        self._add_status_codes(
            pattern=DOWNLOADER_STATUS_CODES_ERRORS, target=self.errors
        )

    def _add_status_codes(self, pattern, target):
        for code, counter in self._get_response_codes(pattern).items():
            target.add_value(code, counter.count)

    def _get_response_codes(self, codes=None):
        codes = codes or ["[^/]+"]
        return_codes = {}
        for code in codes:
            return_codes.update(self._get_response_code(code))
        return return_codes

    def _get_response_code(self, code):
        return dict(
            [
                (code, PercentCounter(count, self.count))
                for count, code in self._stats_analyzer.search(
                    pattern=DOWNLOADER_RESPONSE_STATUS + ("(%s)$" % code),
                    include_matches=True,
                ).values()
            ]
        )


class SpiderMonitorMixin(StatsMonitorMixin, JobMonitorMixin):
    @property
    def crawler(self):
        if not self.data.crawler:
            raise NotConfigured("Crawler not available!")
        return self.data.crawler

    @property
    def spider(self):
        if not self.data.spider:
            raise NotConfigured("Spider not available!")
        return self.data.spider

    @property
    def responses(self):
        if not hasattr(self, "_responses"):
            self._responses = ResponsesInfo(self.stats)
        return self._responses
