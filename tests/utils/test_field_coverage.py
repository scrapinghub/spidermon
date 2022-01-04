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
