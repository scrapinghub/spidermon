from __future__ import absolute_import

from scrapy import signals
from scrapy.utils.misc import load_object
from scrapy.exceptions import NotConfigured
from twisted.internet import reactor

from spidermon import MonitorSuite
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner
from spidermon.utils.hubstorage import hs
from spidermon.python import factory
from spidermon.python.monitors import ExpressionsMonitor


class Spidermon(object):

    def __init__(self, crawler,
                 spider_opened_suites=None, spider_closed_suites=None,
                 spider_opened_expression_suites=None, spider_closed_expression_suites=None,
                 expressions_monitor_class=None,
                 periodic_suites=None, periodic_time=None):
        if not crawler.settings.getbool('SPIDERMON_ENABLED'):
            raise NotConfigured
        self.crawler = crawler

        self.spider_opened_suites = [self.load_suite(s) for s in spider_opened_suites or []]
        self.spider_opened_suites += [self.load_expression_suite(s, expressions_monitor_class)
                                      for s in spider_opened_expression_suites or []]

        self.spider_closed_suites = [self.load_suite(s) for s in spider_closed_suites or []]
        self.spider_closed_suites += [self.load_expression_suite(s, expressions_monitor_class)
                                      for s in spider_closed_expression_suites or []]

        self.periodic_suites = [self.load_suite(s) for s in periodic_suites or []]
        self.periodic_time = periodic_time

    def load_suite(self, suite_to_load):
        try:
            suite_class = load_object(suite_to_load)
        except Exception as e:
            raise e  # TO-DO
        if not issubclass(suite_class, MonitorSuite):
            raise Exception  # TO-DO
        return suite_class(crawler=self.crawler)

    def load_expression_suite(self, suite_to_load, monitor_class=None):
        if monitor_class:
            monitor_class = load_object(monitor_class)
        else:
            monitor_class = ExpressionsMonitor
        monitor = factory.create_monitor_class_from_dict(
            monitor_dict=suite_to_load,
            monitor_class=monitor_class
        )
        suite = MonitorSuite(crawler=self.crawler)
        suite.add_monitor(monitor)
        return suite

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(
            crawler=crawler,
            spider_opened_suites=crawler.settings.getlist('SPIDERMON_SPIDER_OPEN_MONITORS'),
            spider_closed_suites=crawler.settings.getlist('SPIDERMON_SPIDER_CLOSE_MONITORS'),
            spider_opened_expression_suites=crawler.settings.getlist('SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS'),
            spider_closed_expression_suites=crawler.settings.getlist('SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS'),
            expressions_monitor_class=crawler.settings.get('SPIDERMON_EXPRESSIONS_MONITOR_CLASS'),
            periodic_suites=crawler.settings.getlist('SPIDERMON_PERIODIC_MONITORS'),
            periodic_time=crawler.settings.getfloat('SPIDERMON_PERIODIC_TIME')
        )
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_opened(self, spider):
        self._run_suites(spider, self.spider_opened_suites)
        if self.periodic_time:
            reactor.callLater(self.periodic_time, self._run_periodic_suites, spider)

    def spider_closed(self, spider):
        self._run_suites(spider, self.spider_closed_suites)

    def _run_periodic_suites(self, spider):
        self._run_suites(spider, self.periodic_suites)
        reactor.callLater(self.periodic_time, self._run_periodic_suites, spider)

    def _run_suites(self, spider, suites):
        data = self._generate_data_for_spider(spider)
        for suite in suites:
            runner = SpiderMonitorRunner(spider=spider)
            runner.run(suite, **data)

    def _generate_data_for_spider(self, spider):
        return {
            'stats': self.crawler.stats.get_stats(spider),
            'crawler': self.crawler,
            'spider': spider,
            'job': hs.job if hs.available else None,
        }
