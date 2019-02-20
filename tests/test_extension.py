from unittest import mock
import pytest

from scrapy.crawler import Crawler
from scrapy import Spider
from spidermon.contrib.scrapy.extensions import Spidermon


@pytest.fixture
def spidermon_enabled_settings():
    return {
        'SPIDERMON_ENABLED': True,
        'EXTENSIONS': {
            'spidermon.contrib.scrapy.extensions.Spidermon': 500,
        }
    }


@pytest.fixture
def crawler(spidermon_enabled_settings):
    crawler = Crawler(Spider, settings=spidermon_enabled_settings)
    crawler.spider = Spider('dummy')
    return crawler


def test_engine_stopped_suites_should_run(crawler):
    "The suites defined at engine_stopped_suites should be loaded and run """
    engine_stopped_suites = [
        'tests.fixtures.suites.Suite01'
    ]
    spidermon = Spidermon(crawler, engine_stopped_suites=engine_stopped_suites)
    spidermon.engine_stopped_suites[0].run = mock.MagicMock()
    spidermon.engine_stopped()
    assert spidermon.engine_stopped_suites[0].__class__.__name__ == 'Suite01'
    assert spidermon.engine_stopped_suites[0].run.called
