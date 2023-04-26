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

            item_type_total = stats.get(f"spidermon_item_scraped_count/{item_type}")

            if "_items" in item_key:
                if item_key.endswith("_items"):
                    continue

                levels = item_key.split("/_items/")

                root_field_type_total = stats.get(
                    f"spidermon_item_scraped_count/{item_type}/{'/_items/'.join(levels[:-1])}/_items"
                )

                item_field_coverage = value / root_field_type_total
                global_field_coverage = value / item_type_total

                coverage[
                    f"spidermon_field_coverage/{item_type}/{'/'.join(levels)}"
                ] = global_field_coverage

                coverage[
                    f"spidermon_field_coverage/{item_type}/{'/_items/'.join(levels)}"
                ] = item_field_coverage

            else:
                field_coverage = value / item_type_total

                coverage[
                    f"spidermon_field_coverage/{item_type}/{item_key}"
                ] = field_coverage

    return coverage
