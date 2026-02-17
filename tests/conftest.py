pytest_plugins = "spidermon.contrib.pytest.plugins.filter_monitors"

try:
    import scrapy  # noqa: F401
except ImportError:
    pass
else:
    from typing import Any

    import pytest
    from scrapy import Spider
    from scrapy.crawler import Crawler
    from scrapy.statscollectors import MemoryStatsCollector

    @pytest.fixture
    def get_crawler():
        def _crawler(extended_settings: dict[str, Any] | None = None):
            extended_settings = extended_settings or {}
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
