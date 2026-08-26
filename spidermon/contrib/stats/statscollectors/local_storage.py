from __future__ import annotations

import logging
import pickle
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING

from scrapy.exceptions import NotConfigured
from scrapy.statscollectors import StatsCollector
from scrapy.utils.project import data_path

from spidermon.contrib.utils.spider import get_spider_name

if TYPE_CHECKING:
    from scrapy import Spider

logger = logging.getLogger(__name__)


class LocalStorageStatsHistoryCollector(StatsCollector):
    def _stats_location(self, spider):
        statsdir = data_path("stats", createdir=True)
        spider_name = get_spider_name(spider)
        return Path(statsdir) / f"{spider_name}_stats_history"

    def open_spider(self, spider: Spider | None = None):
        spider = spider or self._crawler.spider

        max_stored_stats = spider.crawler.settings.getint(
            "SPIDERMON_MAX_STORED_STATS",
            default=100,
        )

        try:
            stats_location = self._stats_location(spider)
        except NotConfigured:
            logger.warning(
                "Could not find a scrapy.cfg file, so stats history will not "
                "be persisted to disk for this run."
            )
            spider.stats_history = deque(maxlen=max_stored_stats)
            return

        if stats_location.is_file():
            with stats_location.open("rb") as stats_file:
                _stats_history = pickle.load(stats_file)  # noqa: S301
        else:
            _stats_history = deque(maxlen=max_stored_stats)

        if _stats_history.maxlen != max_stored_stats:
            _stats_history = deque(_stats_history, maxlen=max_stored_stats)

        spider.stats_history = _stats_history

    def _persist_stats(self, stats, spider=None):
        spider = spider or self._crawler.spider

        try:
            stats_location = self._stats_location(spider)
        except NotConfigured:
            return

        spider.stats_history.appendleft(self._stats)
        with stats_location.open("wb") as stats_file:
            pickle.dump(spider.stats_history, stats_file)
