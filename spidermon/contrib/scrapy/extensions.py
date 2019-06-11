from __future__ import absolute_import

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.utils.misc import load_object
from twisted.internet.task import LoopingCall

from spidermon import MonitorSuite
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner
from spidermon.python import factory
from spidermon.python.monitors import ExpressionsMonitor
from spidermon.utils.hubstorage import hs


class Spidermon(object):
    def __init__(
        self,
        crawler,
        spider_opened_suites=None,
        spider_closed_suites=None,
        engine_stopped_suites=None,
        spider_opened_expression_suites=None,
        spider_closed_expression_suites=None,
        engine_stopped_expression_suites=None,
        expressions_monitor_class=None,
        periodic_suites=None,
    ):
        if not crawler.settings.getbool("SPIDERMON_ENABLED"):
            raise NotConfigured
        self.crawler = crawler

        self.spider_opened_suites = [
            self.load_suite(s) for s in spider_opened_suites or []
        ]
        self.spider_opened_suites += [
            self.load_expression_suite(s, expressions_monitor_class)
            for s in spider_opened_expression_suites or []
        ]

        self.spider_closed_suites = [
            self.load_suite(s) for s in spider_closed_suites or []
        ]
        self.spider_closed_suites += [
            self.load_expression_suite(s, expressions_monitor_class)
            for s in spider_closed_expression_suites or []
        ]

        self.engine_stopped_suites = [
            self.load_suite(s) for s in engine_stopped_suites or []
        ]
        self.engine_stopped_suites += [
            self.load_expression_suite(s, expressions_monitor_class)
            for s in engine_stopped_expression_suites or []
        ]

        self.periodic_suites = periodic_suites or {}
        self.periodic_tasks = {}

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
            monitor_dict=suite_to_load, monitor_class=monitor_class
        )
        suite = MonitorSuite(crawler=self.crawler)
        suite.add_monitor(monitor)
        return suite

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(
            crawler=crawler,
            spider_opened_suites=crawler.settings.getlist(
                "SPIDERMON_SPIDER_OPEN_MONITORS"
            ),
            spider_closed_suites=crawler.settings.getlist(
                "SPIDERMON_SPIDER_CLOSE_MONITORS"
            ),
            engine_stopped_suites=crawler.settings.getlist(
                "SPIDERMON_ENGINE_STOP_MONITORS"
            ),
            spider_opened_expression_suites=crawler.settings.getlist(
                "SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS"
            ),
            spider_closed_expression_suites=crawler.settings.getlist(
                "SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS"
            ),
            engine_stopped_expression_suites=crawler.settings.getlist(
                "SPIDERMON_ENGINE_STOP_EXPRESSION_MONITORS"
            ),
            expressions_monitor_class=crawler.settings.get(
                "SPIDERMON_EXPRESSIONS_MONITOR_CLASS"
            ),
            periodic_suites=crawler.settings.getdict("SPIDERMON_PERIODIC_MONITORS"),
        )
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.engine_stopped, signal=signals.engine_stopped)
        return ext

    def spider_opened(self, spider):
        self._run_suites(spider, self.spider_opened_suites)
        self.periodic_tasks[spider] = []
        for suite, time in self.periodic_suites.items():
            task = LoopingCall(self._run_periodic_suites, spider, [suite])
            self.periodic_tasks[spider].append(task)
            task.start(time, now=False)

    def spider_closed(self, spider):
        self._run_suites(spider, self.spider_closed_suites)
        for task in self.periodic_tasks[spider]:
            task.stop()

    def engine_stopped(self):
        spider = self.crawler.spider
        self._run_suites(spider, self.engine_stopped_suites)

    def _run_periodic_suites(self, spider, suites):
        suites = [self.load_suite(s) for s in suites]
        self._run_suites(spider, suites)

    def _run_suites(self, spider, suites):
        data = self._generate_data_for_spider(spider)
        for suite in suites:
            runner = SpiderMonitorRunner(spider=spider)
            runner.run(suite, **data)

    def _generate_data_for_spider(self, spider):
        return {
            "stats": self.crawler.stats.get_stats(spider),
            "stats_history": spider.stats_history
            if hasattr(spider, "stats_history")
            else [],
            "crawler": self.crawler,
            "spider": spider,
            "job": hs.job if hs.available else None,
        }
