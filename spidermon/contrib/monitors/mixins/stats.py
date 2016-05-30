from spidermon.exceptions import NotConfigured


class StatsMonitorMixin(object):
    @property
    def stats(self):
        if not self.data.stats:
            raise NotConfigured('Stats not available!')
        return self.data.stats

    @property
    def oldstats(self):
        return self.data.oldstats
