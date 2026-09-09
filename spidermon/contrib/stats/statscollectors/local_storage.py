from __future__ import annotations

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


class LocalStorageStatsHistoryCollector(StatsCollector):
    def _stats_location(self, spider):
        statsdir = data_path("stats", createdir=True)
        spider_name = get_spider_name(spider)
        return Path(statsdir) / f"{spider_name}_stats_history"

    def open_spider(self, spider: Spider | None = None):
        spider = spider or self._crawler.spider

        assert spider
        assert spider.crawler
        max_stored_stats = spider.crawler.settings.getint(
            "SPIDERMON_MAX_STORED_STATS",
            default=100,
        )

        try:
            stats_location = self._stats_location(spider)
        except NotConfigured as error:
            raise NotConfigured(
                f"{error}. {type(self).__name__} stores stats history in the "
                f"project data dir, so it needs a scrapy.cfg file in the "
                f"working directory or one of its parents. Add one, or use a "
                f"different STATS_CLASS."
            ) from error

        if stats_location.is_file():
            with stats_location.open("rb") as stats_file:
                _stats_history = pickle.load(stats_file)  # noqa: S301
        else:
            _stats_history = deque(maxlen=max_stored_stats)

        if _stats_history.maxlen != max_stored_stats:
            _stats_history = deque(_stats_history, maxlen=max_stored_stats)

        spider.stats_history = _stats_history  # type: ignore[attr-defined]

    def _persist_stats(self, stats, spider=None):
        spider = spider or self._crawler.spider
        stats_location = self._stats_location(spider)

        spider.stats_history.appendleft(self._stats)
        with stats_location.open("wb") as stats_file:
            pickle.dump(spider.stats_history, stats_file)
