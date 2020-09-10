from spidermon.exceptions import NotConfigured


class StatsMonitorMixin:
    @property
    def stats(self):
        if not self.data.stats:
            raise NotConfigured("Stats not available!")
        return self.data.stats
