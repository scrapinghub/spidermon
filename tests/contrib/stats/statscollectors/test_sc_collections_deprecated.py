import pytest

pytest.importorskip("scrapy")


def test_deprecated():
    with pytest.warns(
        DeprecationWarning,
        match="spidermon.contrib.stats.statscollectors.sc_collections",
    ):
        from spidermon.contrib.stats.statscollectors import (  # noqa: PLC0415
            sc_collections,
        )

    assert sc_collections.ScrapyCloudCollectionsStatsHistoryCollector is not None
