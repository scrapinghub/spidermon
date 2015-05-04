from scrapy import signals
from scrapy.utils.misc import load_object

from spidermon import MonitorSuite
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner


class Spidermon(object):

    def __init__(self, stats, spider_close_monitors):
        self.stats = stats
        self.spider_close_suites = [self.load_suite(s) for s in spider_close_monitors]

    def load_suite(self, suite_to_load):
        try:
            suite_class = load_object(suite_to_load)
        except Exception, e:
            raise e  # TO-DO
        if not issubclass(suite_class, MonitorSuite):
            raise Exception  # TO-DO
        return suite_class()


    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(
            stats=crawler.stats,
            spider_close_monitors=crawler.settings.getlist('SPIDERMON_SPIDER_CLOSE_MONITORS'),
        )
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_closed(self, spider):
        stats = self.stats.get_stats(spider)
        for suite in self.spider_close_suites:
            runner = SpiderMonitorRunner(spider=spider)
            runner.run(suite, data={'stats': stats})
