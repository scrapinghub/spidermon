import warnings

from spidermon.contrib.zyte.actions.jobs.tags import (  # noqa: F401
    AddJobTags,
    JobTagsAction,
    RemoveJobTags,
)

warnings.warn(
    "spidermon.contrib.actions.jobs.tags is deprecated, import from "
    "spidermon.contrib.zyte.actions.jobs.tags instead.",
    DeprecationWarning,
    stacklevel=2,
)
