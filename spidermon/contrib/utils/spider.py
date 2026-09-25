from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scrapy import Spider


def get_spider_name(spider: Spider) -> str:
    return os.getenv("SHUB_VIRTUAL_SPIDER") or spider.name
