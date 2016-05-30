from scrapy import signals
from scrapy.utils.misc import load_object

from spidermon import MonitorSuite
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner
from spidermon.utils.hubstorage import hs
from spidermon.utils import oldstats
from spidermon.python import factory
from spidermon.python.monitors import ExpressionsMonitor

from spidermon.contrib.actions.slack.notifiers import SendSlackMessageSpiderFinished
from spidermon.contrib.actions.reports.s3 import CreateS3Report


class Spidermon(object):

    def __init__(self, crawler,
                 spider_opened_suites=None, spider_closed_suites=None,
                 spider_opened_expression_suites=None, spider_closed_expression_suites=None,
                 expressions_monitor_class=None):
        self.crawler = crawler

        self.spider_opened_suites = [self.load_suite(s) for s in spider_opened_suites or []]
        self.spider_opened_suites += [self.load_expression_suite(s, expressions_monitor_class)
                                      for s in spider_opened_expression_suites or []]

        self.spider_closed_suites = [self.load_suite(s) for s in spider_closed_suites or []]
        self.spider_closed_suites += [self.load_expression_suite(s, expressions_monitor_class)
                                      for s in spider_closed_expression_suites or []]

    def load_suite(self, suite_to_load):
        try:
            suite_class = load_object(suite_to_load)
        except Exception, e:
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
        #suite.add_monitors_finished_action(CreateS3Report)
        #suite.add_monitors_finished_action(SendSlackMessageSpiderFinished)
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
        )
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_opened(self, spider):
        self._run_suites(spider, self.spider_opened_suites)

    def spider_closed(self, spider):
        self._run_suites(spider, self.spider_closed_suites)

    def _run_suites(self, spider, suites):
        data = self._generate_data_for_spider(spider)
        for suite in suites:
            runner = SpiderMonitorRunner(spider=spider)
            runner.run(suite, **data)
        oldstats.persist(data['stats'])

    def _generate_data_for_spider(self, spider):
        return {
            'stats': self.crawler.stats.get_stats(spider),
            'oldstats': oldstats.load(),
            'crawler': self.crawler,
            'spider': spider,
            'job': hs.job if hs.available else None,
        }
