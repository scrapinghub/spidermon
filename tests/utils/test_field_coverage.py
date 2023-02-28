from spidermon.utils.field_coverage import calculate_field_coverage


def test_calculate_field_coverage_from_stats():
    spider_stats = {
        "finish_reason": "finished",
        "spidermon_item_scraped_count": 100,
        "spidermon_item_scraped_count/dict": 100,
        "spidermon_item_scraped_count/dict/author": 100,
        "spidermon_item_scraped_count/dict/author/author_url": 64,
        "spidermon_item_scraped_count/dict/author/name": 100,
        "spidermon_item_scraped_count/dict/quote": 50,
        "spidermon_item_scraped_count/dict/tags": 100,
    }

    expected_coverage = {
        "spidermon_field_coverage/dict/author": 1.0,
        "spidermon_field_coverage/dict/author/author_url": 0.64,
        "spidermon_field_coverage/dict/author/name": 1.0,
        "spidermon_field_coverage/dict/quote": 0.5,
        "spidermon_field_coverage/dict/tags": 1.0,
    }

    coverage = calculate_field_coverage(spider_stats)

    assert coverage == expected_coverage


def test_calculate_field_coverage_from_stats_with_nested_fields():
    spider_stats = {
        "finish_reason": "finished",
        "spidermon_item_scraped_count": 100,
        "spidermon_item_scraped_count/dict": 100,
        "spidermon_item_scraped_count/dict/field1": 100,
        "spidermon_item_scraped_count/dict/field2": 90,
        "spidermon_item_scraped_count/dict/field2/_items": 1000,
        "spidermon_item_scraped_count/dict/field2/_items/nested_field1": 550,
        "spidermon_item_scraped_count/dict/field2/_items/nested_field2": 1000,
        "spidermon_item_scraped_count/dict/field2/_items/nested_field3": 300,
        "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items": 500,
        "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field1": 500,
        "spidermon_item_scraped_count/dict/field2/_items/nested_field3/_items/deep_field2": 250,
        "spidermon_item_scraped_count/dict/field2/_items/nested_field4": 500,
        "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field1": 500,
        "spidermon_item_scraped_count/dict/field2/_items/nested_field4/deep_field2": 250,
    }

    expected_coverage = {
        "spidermon_field_coverage/dict/field1": 1.0,
        "spidermon_field_coverage/dict/field2": 0.9,
        "spidermon_field_coverage/dict/field2/_items/nested_field1": 0.55,
        "spidermon_field_coverage/dict/field2/_items/nested_field2": 1.0,
        "spidermon_field_coverage/dict/field2/_items/nested_field3": 0.3,
        "spidermon_field_coverage/dict/field2/_items/nested_field3/_items/deep_field1": 1.0,
        "spidermon_field_coverage/dict/field2/_items/nested_field3/_items/deep_field2": 0.5,
        "spidermon_field_coverage/dict/field2/_items/nested_field4": 0.5,
        "spidermon_field_coverage/dict/field2/_items/nested_field4/deep_field1": 0.5,
        "spidermon_field_coverage/dict/field2/_items/nested_field4/deep_field2": 0.25,
        "spidermon_field_coverage/dict/field2/nested_field1": 5.5,
        "spidermon_field_coverage/dict/field2/nested_field2": 10.0,
        "spidermon_field_coverage/dict/field2/nested_field3": 3.0,
        "spidermon_field_coverage/dict/field2/nested_field3/deep_field1": 5.0,
        "spidermon_field_coverage/dict/field2/nested_field3/deep_field2": 2.5,
        "spidermon_field_coverage/dict/field2/nested_field4": 5.0,
        "spidermon_field_coverage/dict/field2/nested_field4/deep_field1": 5.0,
        "spidermon_field_coverage/dict/field2/nested_field4/deep_field2": 2.5,
    }

    coverage = calculate_field_coverage(spider_stats)

    assert coverage == expected_coverage
