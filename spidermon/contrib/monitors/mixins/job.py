from spidermon.exceptions import NotConfigured


class JobMonitorMixin:
    """Adds a ``job`` property to a monitor, for monitors that check a Scrapy Cloud job."""

    @property
    def job(self):
        """The Scrapy Cloud job being monitored."""
        if not self.data.job:
            raise NotConfigured("Job not available!")
        return self.data.job
