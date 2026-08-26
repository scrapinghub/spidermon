import warnings

from spidermon.contrib.zyte.utils import Client  # noqa: F401

warnings.warn(
    "spidermon.utils.zyte is deprecated, import Client from "
    "spidermon.contrib.zyte.utils instead.",
    DeprecationWarning,
    stacklevel=2,
)
