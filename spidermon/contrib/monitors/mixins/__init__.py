import warnings

from .spider import SpiderMonitorMixin
from .stats import StatsMonitorMixin
from .validation import ValidationMonitorMixin

__all__ = [
    "JobMonitorMixin",
    "SpiderMonitorMixin",
    "StatsMonitorMixin",
    "ValidationMonitorMixin",
]


def __getattr__(name):
    if name == "JobMonitorMixin":
        from spidermon.contrib.zyte.monitors.mixins.job import (  # noqa: PLC0415
            JobMonitorMixin,
        )

        warnings.warn(
            "spidermon.contrib.monitors.mixins.JobMonitorMixin is deprecated, "
            "import it from spidermon.contrib.zyte.monitors.mixins.job instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return JobMonitorMixin
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
