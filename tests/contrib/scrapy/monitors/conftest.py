import pytest

from scrapy import Spider
from scrapy.crawler import Crawler
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner


@pytest.fixture
def make_data(request):
    def _make_data(settings=None):
        crawler = Crawler(Spider, settings=settings)
        spider = Spider.from_crawler(crawler, name="dummy")
        return {
            "stats": crawler.stats.get_stats(),
            "crawler": crawler,
            "spider": spider,
            "runner": SpiderMonitorRunner(spider=spider),
            "job": None,
        }

    return _make_data
