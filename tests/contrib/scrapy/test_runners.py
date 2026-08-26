import logging

try:
    import scrapy  # noqa: F401
except ImportError:
    pass
else:
    from scrapy import Spider
    from scrapy.crawler import Crawler
    from scrapy.statscollectors import MemoryStatsCollector

    from spidermon import Monitor, MonitorSuite, monitors
    from spidermon.contrib.scrapy.runners import SpiderMonitorRunner
    from spidermon.core.actions import Action

    class LowLevelFailingMonitor(Monitor):
        @monitors.level.low
        def test_fails(self):
            self.fail("low level failure")

    class DefaultLevelFailingMonitor(Monitor):
        def test_fails(self):
            self.fail("default level failure")

    class PassingMonitor(Monitor):
        def test_passes(self):
            pass

    class FailingAction(Action):
        def run_action(self):
            raise RuntimeError("action failure")

    def test_write_errors_uses_monitor_level(caplog):
        crawler = Crawler(Spider)
        crawler.stats = MemoryStatsCollector(crawler)
        spider = Spider("dummy")
        suite = MonitorSuite(
            monitors=[LowLevelFailingMonitor, DefaultLevelFailingMonitor],
        )

        with caplog.at_level(logging.DEBUG):
            SpiderMonitorRunner(spider=spider).run(
                suite,
                stats=crawler.stats.get_stats(),
            )

        logged_levels = {record.levelno for record in caplog.records}
        assert logging.WARNING in logged_levels
        assert logging.ERROR in logged_levels

    def test_write_errors_handles_action_without_level(caplog):
        crawler = Crawler(Spider)
        crawler.stats = MemoryStatsCollector(crawler)
        spider = Spider("dummy")
        suite = MonitorSuite(
            monitors=[PassingMonitor],
            monitors_finished_actions=[FailingAction],
        )

        with caplog.at_level(logging.DEBUG):
            SpiderMonitorRunner(spider=spider).run(
                suite,
                stats=crawler.stats.get_stats(),
            )

        logged_levels = {record.levelno for record in caplog.records}
        assert logging.ERROR in logged_levels
