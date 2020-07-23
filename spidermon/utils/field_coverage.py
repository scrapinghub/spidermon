import re


def calculate_field_coverage(stats):
    coverage = {}
    for key, value in stats.items():
        if not key.startswith("spidermon_item_scraped_count"):
            continue

        item_type_m = re.search(
            r"spidermon_item_scraped_count\/(?P<item_type>\w+)\/(?P<item_key>.*)", key
        )
        if item_type_m:
            item_type = item_type_m.group(1)
            item_key = item_type_m.group(2)

            item_type_total = stats.get(
                "spidermon_item_scraped_count/{}".format(item_type)
            )
            field_coverage = value / item_type_total

            coverage[
                "spidermon_field_coverage/{}/{}".format(item_type, item_key)
            ] = field_coverage

    return coverage
