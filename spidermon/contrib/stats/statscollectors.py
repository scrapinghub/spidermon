import os
import pickle
from collections import deque

from scrapy.statscollectors import StatsCollector
from scrapy.utils.project import data_path


class LocalStorageStatsHistoryCollector(StatsCollector):
    def __init__(self, crawler):
        self._dump = crawler.settings.getbool("STATS_DUMP")
        self._stats = {}
        self._statsdir = data_path("stats", createdir=True)

    def open_spider(self, spider):
        stats_location = os.path.join(
            self._statsdir, "{}_stats_history".format(spider.name)
        )
        if os.path.isfile(stats_location):
            with open(stats_location, "rb") as stats_file:
                _stats_history = pickle.load(stats_file)
        else:
            max_stored_stats = spider.crawler.settings.getint(
                "SPIDERMON_MAX_STORED_STATS", default=100
            )
            _stats_history = deque([], maxlen=max_stored_stats)
        spider.stats_history = _stats_history

    def _persist_stats(self, stats, spider):
        spider.stats_history.appendleft(self._stats)
        stats_location = os.path.join(
            self._statsdir, "{}_stats_history".format(spider.name)
        )
        with open(stats_location, "wb") as stats_file:
            pickle.dump(spider.stats_history, stats_file)
