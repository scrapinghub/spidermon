import pytest
from scrapy.utils.test import get_crawler
from spidermon.contrib.scrapy.pipelines import (
    ItemValidationPipeline,
    PassThroughPipeline,
)


@pytest.fixture
def spidermon_enabled_settings():
    return {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
    }


def test_spidermon_enabled_return_item_validation_pipeline():
    settings = {
        "SPIDERMON_ENABLED": True,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_VALIDATION_SCHEMAS": [{"dummy": "schema"}],
    }
    crawler = get_crawler(settings_dict=settings)
    pipeline = ItemValidationPipeline.from_crawler(crawler)
    assert isinstance(pipeline, ItemValidationPipeline)


def test_spidermon_disabled_return_pass_through_pipeline():
    settings = {
        "SPIDERMON_ENABLED": False,
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_VALIDATION_SCHEMAS": [{"dummy": "schema"}],
    }
    crawler = get_crawler(settings_dict=settings)
    pipeline = ItemValidationPipeline.from_crawler(crawler)
    assert isinstance(pipeline, PassThroughPipeline)


def test_return_pass_through_pipeline_if_spidermon_enabled_setting_is_not_provided():
    settings = {
        "EXTENSIONS": {"spidermon.contrib.scrapy.extensions.Spidermon": 100},
        "SPIDERMON_VALIDATION_SCHEMAS": [{"dummy": "schema"}],
    }
    crawler = get_crawler(settings_dict=settings)
    pipeline = ItemValidationPipeline.from_crawler(crawler)
    assert isinstance(pipeline, PassThroughPipeline)


def test_pass_through_pipeline():
    pipeline = PassThroughPipeline()
    item = pipeline.process_item({"original": "item"})
    assert item == {"original": "item"}
