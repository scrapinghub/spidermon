import os
import pickle
from collections import deque

from scrapy.statscollectors import StatsCollector
from scrapy.utils.project import data_path


class LocalStorageStatsHistoryCollector(StatsCollector):
    def _stats_location(self, spider):
        statsdir = data_path("stats", createdir=True)
        return os.path.join(statsdir, "{}_stats_history".format(spider.name))

    def open_spider(self, spider):
        stats_location = self._stats_location(spider)

        max_stored_stats = spider.crawler.settings.getint(
            "SPIDERMON_MAX_STORED_STATS", default=100
        )

        if os.path.isfile(stats_location):
            with open(stats_location, "rb") as stats_file:
                _stats_history = pickle.load(stats_file)
        else:
            _stats_history = deque([], maxlen=max_stored_stats)

        if _stats_history.maxlen != max_stored_stats:
            _stats_history = deque(_stats_history, maxlen=max_stored_stats)

        spider.stats_history = _stats_history

    def _persist_stats(self, stats, spider):
        stats_location = self._stats_location(spider)

        spider.stats_history.appendleft(self._stats)
        with open(stats_location, "wb") as stats_file:
            pickle.dump(spider.stats_history, stats_file)
