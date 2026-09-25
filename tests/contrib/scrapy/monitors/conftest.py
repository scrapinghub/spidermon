try:
    import scrapy  # noqa: F401
except ImportError:
    pass
else:
    from collections.abc import Callable
    from typing import Any

    import pytest
    from scrapy import Spider
    from scrapy.crawler import Crawler
    from scrapy.statscollectors import MemoryStatsCollector

    from spidermon.contrib.scrapy.runners import SpiderMonitorRunner

    @pytest.fixture
    def make_data(
        request: pytest.FixtureRequest,
    ) -> Callable[..., dict[str, Any]]:
        def _make_data(settings: dict[str, Any] | None = None) -> dict[str, Any]:
            crawler = Crawler(Spider, settings=settings)
            crawler.stats = MemoryStatsCollector(crawler)
            spider = Spider("dummy")
            return {
                "stats": crawler.stats.get_stats(),
                "crawler": crawler,
                "spider": spider,
                "runner": SpiderMonitorRunner(spider=spider),
                "job": None,
            }

        return _make_data
