from spidermon.contrib.scrapy.pipelines import ItemValidationPipeline
from scrapy import Item, Field
from scrapy.statscollectors import MemoryStatsCollector
from scrapy.spiders import Spider
from scrapy.utils.test import get_crawler
from spidermon.contrib.validation import JSONSchemaValidator


class Tree(Item):
    child = Field()


def test_can_process_items_with_nested_items():
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema",
        "required": [
            "child",
        ],
        "type": "object",
        "properties": {
            "child": {
                "type": "object",
            }
        }
    }

    stats = MemoryStatsCollector(get_crawler(Spider))
    json_schema_validator = JSONSchemaValidator(schema)

    item = Tree()
    item['child'] = Tree()

    validators = {Tree.__name__: [json_schema_validator]}
    pipeline = ItemValidationPipeline(validators, stats)
    pipeline.process_item(item, None)

    assert 'spidermon/validation/items/errors' not in stats.get_stats()

