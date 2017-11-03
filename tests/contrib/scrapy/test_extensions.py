from __future__ import absolute_import
import json
from functools import partial
from unittest import TestCase

from scrapy.utils.test import get_crawler
from scrapy import Spider

from spidermon.contrib.scrapy.extensions import Spidermon
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner


class TestSpiderMonitorRunner(SpiderMonitorRunner):
    def run_monitors(self):
        self.result.next_step()
        res = self.suite.run(self.result)
        raise AssertionError((res.failures, res.errors))


def _test_run_suites(self, spider, suites):
    data = self._generate_data_for_spider(spider)
    for suite in suites:
        runner = TestSpiderMonitorRunner(spider=spider)
        runner.run(suite, **data)


class TestData(object):
    def __init__(self, expression, stats={}, settings={}, expected_error=None):
        self.stats = stats
        self.expression = expression
        self.settings = settings
        self.expected_error = expected_error


class ExpressionMonitorsTesting(TestCase):
    '''
    Tests if expression monitors, which defined in settings, properly configured:
        - SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS,
        - SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS,

    Test case only for expression monitors firing at the spider's opening, but at
    closing time logic are the same, as well as way of loading test suites.

    Makes sure that all context components are available for usage, these are
    supposed to be configured and existed in the context of expressions:
        - stats,
        - crawler,
        - spider,
        - job,
        - validation,
        - responses

    NotConfigured error should also fire only in appropriate time: when interpreter
    evaluates expressions.
    '''

    spider_name = 'test'

    def run_test(self, **kwargs):
        dt = TestData(**kwargs)
        settings = {
            'SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS': [{
                'tests': [{
                    'expression': dt.expression,
                }]
            }]
        }
        settings.update(dt.settings)
        crawler = get_crawler(settings_dict=settings)
        crawler.stats.get_stats = lambda _: dt.stats
        spidermon = Spidermon.from_crawler(crawler)
        spider = Spider(name=self.spider_name)

        # mocking, to see test results via raising AssertionError exception
        # with failures and errors as results
        spidermon._run_suites = partial(_test_run_suites, spidermon)

        try:
            spidermon.spider_opened(spider)
        except AssertionError as e:
            failures, errors = e.message
            for f in failures:
                _, trace = f
                raise AssertionError(trace)
            for e in errors:
                _, trace = e
                if dt.expected_error and dt.expected_error in trace:
                    dt.expected_error = None
                else:
                    raise AssertionError(trace)
            if dt.expected_error:
                raise AssertionError(
                    'Expected error <{}> was not raised'.format(dt.expected_error))


    def test_stats_ready(self):
        self.run_test(
            stats={"finish_reason": "dead"},
            expression="stats.finish_reason == 'dead'",
        )

    def test_stats_not_configured(self):
        self.run_test(
            expression="stats.finish_reason == 'dead'",
            expected_error='NotConfigured',
        )

    def test_crawler_ready(self):
        self.run_test(
            settings={"special_check": "12345"},
            expression="crawler.settings['special_check'] == '12345'",
        )

    def test_spider_ready(self):
        self.run_test(
            expression="spider.name == '{}'".format(self.spider_name),
        )

    def test_responses_ready(self):
        self.run_test(
            stats={"finish_reason": "dead"}, # any stats, responses created from stats
            expression="responses.count == 0",
        )

    def test_responses_not_configured(self):
        self.run_test(
            expression="responses.count == 0",
            expected_error='NotConfigured',
        )

    def test_validation_ready(self):
        self.run_test(
            stats={"finish_reason": "dead"}, # any stats, validation created from stats
            expression="validation.items.count == 0",
        )

    def test_validation_not_configured(self):
        self.run_test(
            expression="validation.items.count == 0",
            expected_error='NotConfigured',
        )

    def test_job_not_configured(self):
        # job is not configured, but existed in the context
        self.run_test(
            expression="job.metadata['finish_reason' == 'dead']",
            expected_error='NotConfigured',
        )

    def test_inappropriate_context(self):
        # expected something like <NameError: name 'foo' is not defined>
        self.run_test(
            expression="foo.bar == 'boo'",
            expected_error='NameError',
        )
