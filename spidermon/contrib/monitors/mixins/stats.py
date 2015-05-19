from spidermon.exceptions import NotConfigured


class StatsMonitorMixin(object):
    @property
    def stats(self):
        if 'stats' not in self.data:
            raise NotConfigured('Stats not available!')
        return self.data.stats
