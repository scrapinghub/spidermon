import logging
import os
from collections import deque

import scrapinghub
from sh_scrapy.stats import HubStorageStatsCollector

logger = logging.getLogger(__name__)


class ScrapyCloudCollectionsStatsHistoryCollector(HubStorageStatsCollector):
    def _open_collection(self, spider):
        sh_client = scrapinghub.ScrapinghubClient()
        proj_id = os.environ.get("SCRAPY_PROJECT_ID")
        if proj_id is None:
            # not running on dash
            return

        project = sh_client.get_project(proj_id)
        collections = project.collections
        stats_location = f"{spider.name}_stats_history"
        store = collections.get_store(stats_location)
        return store

    def open_spider(self, spider):
        super().open_spider(spider)
        self.store = self._open_collection(spider)
        # note that the _open_collection method does not error if collection does not exist yet
        if self.store is None:
            return

        max_stored_stats = spider.crawler.settings.getint(
            "SPIDERMON_MAX_STORED_STATS", default=100
        )

        try:
            stats_history = [d.get("value") for d in self.store.iter()]
            stats_history = deque(stats_history, maxlen=max_stored_stats)
        except scrapinghub.client.exceptions.NotFound:
            # this happens if the stats store has not been created yet
            stats_history = deque([], maxlen=max_stored_stats)

        spider.stats_history = stats_history

    def _persist_stats(self, stats, spider):
        if self.store is None:
            return
        stats_history = spider.stats_history
        stats_history.appendleft(self._stats)
        for index, data in enumerate(stats_history):
            if index == 0:
                job_id = os.environ.get("SCRAPY_JOB", "")
                if job_id:
                    data["job_url"] = f"https://app.zyte.com/p/{job_id}"
            # this will create up to SPIDERMON_MAX_STORED_STATS objects
            # with keys 0 -> SPIDERMON_MAX_STORED_STATS - 1
            self.store.set({"_key": str(index), "value": data})
