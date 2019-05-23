import os
import pickle
from collections import deque

from scrapy.statscollectors import StatsCollector
from scrapy.utils.project import data_path


class LocalStorageStatsHistoryCollector(StatsCollector):
    def __init__(self, crawler):
        super(LocalStorageStatsHistoryCollector, self).__init__(crawler)

        statsdir = data_path("stats", createdir=True)
        self.stats_location = os.path.join(
            statsdir, "{}_stats_history".format(crawler.spider.name)
        )

    def open_spider(self, spider):
        max_stored_stats = spider.crawler.settings.getint(
            "SPIDERMON_MAX_STORED_STATS", default=100
        )

        if os.path.isfile(self.stats_location):
            with open(self.stats_location, "rb") as stats_file:
                _stats_history = pickle.load(stats_file)
        else:
            _stats_history = deque([], maxlen=max_stored_stats)

        if _stats_history.maxlen != max_stored_stats:
            _stats_history = deque([
                stat for stat in _stats_history
            ], maxlen=max_stored_stats)

        spider.stats_history = _stats_history

    def _persist_stats(self, stats, spider):
        spider.stats_history.appendleft(self._stats)
        with open(self.stats_location, "wb") as stats_file:
            pickle.dump(spider.stats_history, stats_file)
