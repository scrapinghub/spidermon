import os


def get_spider_name(spider):
    return os.getenv("SHUB_VIRTUAL_SPIDER") or spider.name
