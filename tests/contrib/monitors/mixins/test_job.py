import pytest

from spidermon.contrib.monitors import mixins


def test_deprecated_module():
    with pytest.warns(
        DeprecationWarning,
        match="spidermon.contrib.monitors.mixins.job",
    ):
        from spidermon.contrib.monitors.mixins import job  # noqa: PLC0415

    assert job.JobMonitorMixin is not None


def test_deprecated_attribute():
    with pytest.warns(
        DeprecationWarning,
        match="spidermon.contrib.monitors.mixins.JobMonitorMixin",
    ):
        assert mixins.JobMonitorMixin is not None
