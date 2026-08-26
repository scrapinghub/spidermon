_NAMES = frozenset(
    {
        "SPIDERMON_JOBS_COMPARISON",
        "SPIDERMON_JOBS_COMPARISON_ARGUMENTS",
        "SPIDERMON_JOBS_COMPARISON_ARGUMENTS_ENABLED",
        "SPIDERMON_JOBS_COMPARISON_CLOSE_REASONS",
        "SPIDERMON_JOBS_COMPARISON_STATES",
        "SPIDERMON_JOBS_COMPARISON_TAGS",
        "SPIDERMON_JOBS_COMPARISON_THRESHOLD",
        "ZyteJobsComparisonMonitor",
    },
)

__all__ = list(_NAMES)


def __getattr__(name):
    if name in _NAMES:
        from . import monitors  # noqa: PLC0415

        return getattr(monitors, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
