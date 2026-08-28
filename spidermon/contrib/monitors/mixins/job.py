import warnings

from spidermon.contrib.zyte.monitors.mixins.job import JobMonitorMixin  # noqa: F401

warnings.warn(
    "spidermon.contrib.monitors.mixins.job is deprecated, import "
    "JobMonitorMixin from spidermon.contrib.zyte.monitors.mixins.job instead.",
    DeprecationWarning,
    stacklevel=2,
)
