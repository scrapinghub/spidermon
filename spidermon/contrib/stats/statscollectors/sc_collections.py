import warnings

from spidermon.contrib.zyte.statscollectors.sc_collections import (  # noqa: F401
    ScrapyCloudCollectionsStatsHistoryCollector,
)

warnings.warn(
    "spidermon.contrib.stats.statscollectors.sc_collections is deprecated, "
    "import ScrapyCloudCollectionsStatsHistoryCollector from "
    "spidermon.contrib.zyte.statscollectors.sc_collections instead.",
    DeprecationWarning,
    stacklevel=2,
)
