from spidermon.exceptions import NotConfigured


class StatsMonitorMixin:
    """Adds a ``stats`` property to a monitor, for monitors that check job stats."""

    @property
    def stats(self):
        """The stats of the job being monitored."""
        if not self.data.stats:
            raise NotConfigured("Stats not available!")
        return self.data.stats
