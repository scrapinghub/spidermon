import datetime
import json
import os

from scrapy.statscollectors import StatsCollector
from scrapy.utils.project import data_path


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


class HistoricalStatsCollector(StatsCollector):
    pass


class LocalStorageHistoricalStatsCollector(HistoricalStatsCollector):
    def __init__(self, crawler):
        self._dump = crawler.settings.getbool("STATS_DUMP")
        self._stats = {}
        self._statsdir = data_path("stats", createdir=True)

    def open_spider(self, spider):
        old_stats = []
        for stats_file in os.listdir(self._statsdir):
            if not os.path.isfile(os.path.join(self._statsdir, stats_file)):
                continue
            with open(os.path.join(self._statsdir, stats_file)) as stats:
                old_stats.append(json.loads(stats.read()))
        spider.old_stats = old_stats

    def _persist_stats(self, stats, spider):
        key = str(int(datetime.datetime.now().timestamp()))
        stats_f = os.path.join(self._statsdir, str(key))
        with open(stats_f, "w") as s_f:
            s_f.write(json.dumps(self._stats, default=json_serial))
