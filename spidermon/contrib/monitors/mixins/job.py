from typing import Any

from spidermon.exceptions import NotConfigured


class JobMonitorMixin:
    """Adds a ``job`` property to a monitor, for monitors that check a Scrapy Cloud job."""

    data: Any

    @property
    def job(self) -> Any:
        """The Scrapy Cloud job being monitored."""
        if not self.data.job:
            raise NotConfigured("Job not available!")
        return self.data.job
