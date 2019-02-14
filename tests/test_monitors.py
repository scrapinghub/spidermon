from scrapy import Spider
from scrapy.crawler import Crawler
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner
from spidermon.contrib.scrapy.monitors import (
    FinishReasonMonitor, ItemCountMonitor, LogMonitor, UnwantedHttpStatus,
    SPIDERMON_MIN_ITEMS, SPIDERMON_EXPECTED_FINISH_REASONS,
    SPIDERMON_MAX_ERROR, SPIDERMON_MAX_UNWANTED_HTTP_CODES)
from spidermon import MonitorSuite


def new_crawler():
    return Crawler(Spider)


def new_suite(monitors):
    return MonitorSuite(monitors=monitors)


def test_needs_to_configure_item_count_monitor():
    """ Should raise an exception when ItemCountMonitor it's not configured """
    crawler = new_crawler()
    spider = Spider('dummy')
    suite = new_suite([ItemCountMonitor, ])
    runner = SpiderMonitorRunner(spider=spider)
    crawler.stats.set_value('item_scraped_count', 10)
    data = {
            'stats': crawler.stats.get_stats(),
            'crawler': crawler,
            'spider': spider,
            'job': None,
    }
    runner.run(suite, **data)
    for r in runner.result.monitor_results:
        assert('spidermon.exceptions.NotConfigured' in r.error)


def test_item_count_monitor_should_fail():
    """ ItemCount should fail when the desired # of items is not extracted """
    crawler = new_crawler()
    spider = Spider('dummy')
    setattr(spider, SPIDERMON_MIN_ITEMS.lower(), 100)
    suite = new_suite([ItemCountMonitor, ])
    runner = SpiderMonitorRunner(spider=spider)
    crawler.stats.set_value('item_scraped_count', 10)
    data = {
            'stats': crawler.stats.get_stats(),
            'crawler': crawler,
            'spider': spider,
            'job': None,
    }
    runner.run(suite, **data)
    for r in runner.result.monitor_results:
        assert('Extracted 10 items, the expected minimum is 100' in r.error)


def test_item_count_monitor_should_pass():
    """ ItemCount should pass when extract the desired amount of items """
    crawler = new_crawler()
    spider = Spider('dummy')
    setattr(spider, SPIDERMON_MIN_ITEMS.lower(), 100)
    suite = new_suite([ItemCountMonitor, ])
    runner = SpiderMonitorRunner(spider=spider)
    crawler.stats.set_value('item_scraped_count', 100)
    data = {
            'stats': crawler.stats.get_stats(),
            'crawler': crawler,
            'spider': spider,
            'job': None,
    }
    runner.run(suite, **data)
    assert(runner.result.monitor_results[0].error is None)


def test_finished_reason_monitor_should_fail():
    """ FinishedReason should fail when spider finished with unexpected
    reason """
    crawler = new_crawler()
    spider = Spider('dummy')
    suite = new_suite([FinishReasonMonitor, ])
    runner = SpiderMonitorRunner(spider=spider)
    crawler.stats.set_value('finish_reason', 'bad_finish')
    data = {
            'stats': crawler.stats.get_stats(),
            'crawler': crawler,
            'spider': spider,
            'job': None,
    }
    runner.run(suite, **data)
    assert('Finished with "bad_finish" the expected reasons' in
           runner.result.monitor_results[0].error)


def test_finished_reason_monitor_should_pass():
    """ FinishedReason should succeed when spider finished with expected
    reason """
    crawler = new_crawler()
    spider = Spider('dummy')
    setattr(spider, SPIDERMON_EXPECTED_FINISH_REASONS.lower(),
            ('special_reason', ))
    suite = new_suite([FinishReasonMonitor, ])
    runner = SpiderMonitorRunner(spider=spider)
    crawler.stats.set_value('finish_reason', 'special_reason')
    data = {
            'stats': crawler.stats.get_stats(),
            'crawler': crawler,
            'spider': spider,
            'job': None,
    }
    runner.run(suite, **data)
    assert(runner.result.monitor_results[0].error is None)


def test_log_monitor_should_fail():
    """ Log should fail if the # of error log messages exceed the limit """
    crawler = new_crawler()
    spider = Spider('dummy')
    suite = new_suite([LogMonitor, ])
    runner = SpiderMonitorRunner(spider=spider)
    crawler.stats.set_value('log_count/ERROR', 2)
    data = {
            'stats': crawler.stats.get_stats(),
            'crawler': crawler,
            'spider': spider,
            'job': None,
    }
    runner.run(suite, **data)
    assert(' Found 2 errors in log' in runner.result.monitor_results[0].error)


def test_log_monitor_should_pass():
    """ Log should pass if the # of error log message DOES NOT
    exceed the limit """
    crawler = new_crawler()
    spider = Spider('dummy')
    setattr(spider, SPIDERMON_MAX_ERROR.lower(), 50)
    suite = new_suite([LogMonitor, ])
    runner = SpiderMonitorRunner(spider=spider)
    crawler.stats.set_value('log_count/ERROR', 2)
    data = {
            'stats': crawler.stats.get_stats(),
            'crawler': crawler,
            'spider': spider,
            'job': None,
    }
    runner.run(suite, **data)
    assert(runner.result.monitor_results[0].error is None)


def test_unwanted_httpcodes_should_fail():
    """Unwanted HTTP Code should fail if # off responses with error status
    codes is higher than expected """
    crawler = new_crawler()
    spider = Spider('dummy')
    suite = new_suite([UnwantedHttpStatus, ])
    runner = SpiderMonitorRunner(spider=spider)
    crawler.stats.set_value('downloader/response_status_count/500', 1)
    data = {
            'stats': crawler.stats.get_stats(),
            'crawler': crawler,
            'spider': spider,
            'job': None,
    }
    runner.run(suite, **data)
    assert('Found 1 Responses with status code=500'
           in runner.result.monitor_results[0].error)


def test_unwanted_httpcodes_should_pass():
    """Unwanted HTTP Code should pass if # off responses with error status
    codes is lower than expected """
    crawler = new_crawler()
    spider = Spider('dummy')
    setattr(spider, SPIDERMON_MAX_UNWANTED_HTTP_CODES.lower(), 100)
    suite = new_suite([UnwantedHttpStatus, ])
    runner = SpiderMonitorRunner(spider=spider)
    crawler.stats.set_value('downloader/response_status_count/500', 99)
    data = {
            'stats': crawler.stats.get_stats(),
            'crawler': crawler,
            'spider': spider,
            'job': None,
    }
    runner.run(suite, **data)
    assert(runner.result.monitor_results[0].error is None)
