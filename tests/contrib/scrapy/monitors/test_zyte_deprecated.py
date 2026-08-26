import pytest

pytest.importorskip("scrapy")

from spidermon.contrib.scrapy import monitors
from spidermon.contrib.scrapy.monitors import monitors as monitors_module


def test_deprecated_attribute():
    with pytest.warns(
        DeprecationWarning,
        match="spidermon.contrib.scrapy.monitors.ZyteJobsComparisonMonitor",
    ):
        assert monitors.ZyteJobsComparisonMonitor is not None


def test_deprecated_submodule_attribute():
    with pytest.warns(
        DeprecationWarning,
        match="spidermon.contrib.scrapy.monitors.monitors.ZyteJobsComparisonMonitor",
    ):
        assert monitors_module.ZyteJobsComparisonMonitor is not None

    with pytest.raises(AttributeError):
        monitors_module.does_not_exist  # noqa: B018
