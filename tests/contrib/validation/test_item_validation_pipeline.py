from collections import defaultdict
from dataclasses import dataclass

import pytest
import scrapy
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


@pytest.fixture
def dummy_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema",
        "type": "object",
        "properties": {
            "foo": {"const": "bar"},
        },
        "required": ["foo"],
        "additionalProperties": False,
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


def test_jsonschema_validation(dummy_schema):
    settings = {
        "SPIDERMON_ENABLED": True,
        "SPIDERMON_VALIDATION_SCHEMAS": [dummy_schema],
        "SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS": True,
    }

    item = {"foo": "bar"}

    crawler = get_crawler(settings_dict=settings)
    pipeline = ItemValidationPipeline.from_crawler(crawler)
    result_item = pipeline.process_item(dict(item), None)
    assert item == result_item

    item = {}
    result_item = pipeline.process_item(dict(item), None)
    assert item != result_item
    assert "_validation" in result_item
    assert not isinstance(result_item["_validation"], defaultdict)
    assert result_item["_validation"]["foo"] == ["Missing required field"]


def test_validation_errors_field(dummy_schema):
    settings = {
        "SPIDERMON_ENABLED": True,
        "SPIDERMON_VALIDATION_SCHEMAS": [dummy_schema],
        "SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS": True,
        "SPIDERMON_VALIDATION_ERRORS_FIELD": "custom_validation_field",
    }

    crawler = get_crawler(settings_dict=settings)
    pipeline = ItemValidationPipeline.from_crawler(crawler)

    # Instantiate validation field if not defined
    item = {"no": "schema"}
    item = pipeline.process_item(item, None)
    assert "custom_validation_field" in item

    # Instantiate validation field if None
    item = {"no": "schema", "custom_validation_field": None}
    item = pipeline.process_item(item, None)
    assert item["custom_validation_field"] is not None


def test_add_error_to_items_undefined_validation_field(dummy_schema):
    settings = {
        "SPIDERMON_ENABLED": True,
        "SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS": True,
        "SPIDERMON_VALIDATION_SCHEMAS": [dummy_schema],
        "SPIDERMON_VALIDATION_ERRORS_FIELD": "custom_validation_field",
    }

    crawler = get_crawler(settings_dict=settings)
    pipeline = ItemValidationPipeline.from_crawler(crawler)

    # Extensible classes like dict support adding additional field
    item = {"foo": "invalid"}
    item = pipeline.process_item(item, None)
    assert "custom_validation_field" in item

    # Non-extensible classes like scrapy.Items and Dataclass raises errors
    class ScrapyItem(scrapy.Item):
        foo = scrapy.Field()

    item = ScrapyItem(foo="invalid")
    # Supports item assignment but field but does not support field
    with pytest.raises(
        KeyError, match="ScrapyItem does not support field: custom_validation_field"
    ):
        item = pipeline.process_item(item, None)

    @dataclass
    class DataclassItem:
        foo: str

    item = DataclassItem(foo="invalid")
    # Supports item assignment but does not support field
    with pytest.raises(KeyError, match="custom_validation_field"):
        item = pipeline.process_item(item, None)


def test_not_configured():
    # No validators
    settings = {
        "SPIDERMON_ENABLED": True,
        "SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS": True,
        "SPIDERMON_VALIDATION_ERRORS_FIELD": "custom_validation_field",
    }
    crawler = get_crawler(settings_dict=settings)
    with pytest.raises(
        scrapy.exceptions.NotConfigured, match="No validators were found"
    ):
        ItemValidationPipeline.from_crawler(crawler)

    # Invalid validator type
    settings = {
        "SPIDERMON_ENABLED": True,
        "SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS": True,
        "SPIDERMON_VALIDATION_SCHEMAS": object(),
        "SPIDERMON_VALIDATION_ERRORS_FIELD": "custom_validation_field",
    }
    crawler = get_crawler(settings_dict=settings)
    with pytest.raises(
        scrapy.exceptions.NotConfigured,
        match=r"Invalid <.*> type for <.*> settings",
    ):
        ItemValidationPipeline.from_crawler(crawler)

    # Invalid schema type
    settings = {
        "SPIDERMON_ENABLED": True,
        "SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS": True,
        "SPIDERMON_VALIDATION_SCHEMAS": [False],
        "SPIDERMON_VALIDATION_ERRORS_FIELD": "custom_validation_field",
    }
    crawler = get_crawler(settings_dict=settings)
    with pytest.raises(
        scrapy.exceptions.NotConfigured,
        match=r"Invalid schema, jsonschemas must be defined as:.*",
    ):
        ItemValidationPipeline.from_crawler(crawler)


def test_drop_invalid_item(dummy_schema):
    settings = {
        "SPIDERMON_ENABLED": True,
        "SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS": True,
        "SPIDERMON_VALIDATION_SCHEMAS": [dummy_schema],
        "SPIDERMON_VALIDATION_DROP_ITEMS_WITH_ERRORS": True,
        "SPIDERMON_VALIDATION_ERRORS_FIELD": "custom_validation_field",
    }

    crawler = get_crawler(settings_dict=settings)
    pipeline = ItemValidationPipeline.from_crawler(crawler)

    item = {"foo": "invalid"}
    with pytest.raises(scrapy.exceptions.DropItem):
        pipeline.process_item(item, None)


def test_ignore_classes_without_schema(dummy_schema):
    settings = {
        "SPIDERMON_ENABLED": True,
        "SPIDERMON_VALIDATION_ADD_ERRORS_TO_ITEMS": True,
        "SPIDERMON_VALIDATION_SCHEMAS": {scrapy.Item: dummy_schema},
        "SPIDERMON_VALIDATION_DROP_ITEMS_WITH_ERRORS": True,
        "SPIDERMON_VALIDATION_ERRORS_FIELD": "custom_validation_field",
    }
    crawler = get_crawler(settings_dict=settings)
    pipeline = ItemValidationPipeline.from_crawler(crawler)

    @dataclass
    class DummyItem:
        foo: str = "bar"

    item = DummyItem()
    pipeline.process_item(item, None)
