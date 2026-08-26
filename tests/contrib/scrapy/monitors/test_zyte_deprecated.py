import pytest

pytest.importorskip("scrapy")

from spidermon.contrib.scrapy import monitors


def test_deprecated_attribute():
    with pytest.warns(
        DeprecationWarning,
        match="spidermon.contrib.scrapy.monitors.ZyteJobsComparisonMonitor",
    ):
        assert monitors.ZyteJobsComparisonMonitor is not None
