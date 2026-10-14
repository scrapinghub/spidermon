from __future__ import annotations

import logging
import os
from collections import deque
from typing import TYPE_CHECKING, Any

import scrapinghub
from sh_scrapy.stats import HubStorageStatsCollector

from spidermon.contrib.utils.spider import get_spider_name

if TYPE_CHECKING:
    from scrapy import Spider
    from scrapy.statscollectors import StatsT

logger = logging.getLogger(__name__)


class ScrapyCloudCollectionsStatsHistoryCollector(HubStorageStatsCollector):  # type: ignore[misc]
    def _open_collection(self, spider: Spider) -> Any:
        sh_client = scrapinghub.ScrapinghubClient()
        proj_id = os.environ.get("SCRAPY_PROJECT_ID")
        if proj_id is None:
            # not running on dash
            return None

        project = sh_client.get_project(proj_id)
        collections = project.collections
        spider_name = get_spider_name(spider)
        stats_location = f"{spider_name}_stats_history"
        return collections.get_store(stats_location)

    def open_spider(self, spider: Spider | None = None) -> None:
        args = [spider] if spider else []
        super().open_spider(*args)
        spider = spider or self._crawler.spider
        self.store = self._open_collection(spider)
        # note that the _open_collection method does not error if collection does not exist yet
        if self.store is None:
            return

        max_stored_stats = spider.crawler.settings.getint(
            "SPIDERMON_MAX_STORED_STATS",
            default=100,
        )

        try:
            stats_history = deque(
                [d.get("value") for d in self.store.iter()], maxlen=max_stored_stats
            )
        except scrapinghub.client.exceptions.NotFound:
            # this happens if the stats store has not been created yet
            stats_history = deque(maxlen=max_stored_stats)

        spider.stats_history = stats_history  # type: ignore[union-attr]

    def _persist_stats(self, stats: StatsT, spider: Spider | None = None) -> None:
        if self.store is None:
            return
        spider = spider or self._crawler.spider
        stats_history = spider.stats_history  # type: ignore[union-attr]
        stats_history.appendleft(self._stats)
        for index, data in enumerate(stats_history):
            if index == 0:
                job_id = os.environ.get("SCRAPY_JOB", "")
                if job_id:
                    data["job_url"] = f"https://app.zyte.com/p/{job_id}"
            # this will create up to SPIDERMON_MAX_STORED_STATS objects
            # with keys 0 -> SPIDERMON_MAX_STORED_STATS - 1
            self.store.set({"_key": str(index), "value": data})
