from spidermon.exceptions import NotConfigured

from .stats import StatsMonitorMixin
from .job import JobMonitorMixin


class SpiderMonitorMixin(StatsMonitorMixin, JobMonitorMixin):
    @property
    def crawler(self):
        if 'crawler' not in self.data:
            raise NotConfigured('Crawler not available!')
        return self.data.crawler

    @property
    def spider(self):
        if 'spider' not in self.data:
            raise NotConfigured('Spider not available!')
        return self.data.spider
