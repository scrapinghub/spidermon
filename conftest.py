import pytest
from scrapy.crawler import Crawler
from scrapy.statscollectors import MemoryStatsCollector
from scrapy import Spider


pytest_plugins = "spidermon.contrib.pytest.plugins.filter_monitors"


@pytest.fixture
def get_crawler():
    def _crawler(extended_settings={}):
        settings = {
            "SPIDERMON_ENABLED": True,
            "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 500},
        }
        settings.update(extended_settings)
        crawler = Crawler(Spider, settings=settings)
        crawler.spider = Spider("dummy")
        crawler.stats = MemoryStatsCollector(crawler)
        return crawler

    return _crawler
