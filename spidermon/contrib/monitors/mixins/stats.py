from __future__ import annotations

from typing import TYPE_CHECKING, Any

from spidermon.exceptions import NotConfigured

if TYPE_CHECKING:
    from spidermon.data import Data


class StatsMonitorMixin:
    """Adds a ``stats`` property to a monitor, for monitors that check job stats."""

    data: Any

    @property
    def stats(self) -> Data:
        """The stats of the job being monitored."""
        if not self.data.stats:
            raise NotConfigured("Stats not available!")
        stats: Data = self.data.stats
        return stats
