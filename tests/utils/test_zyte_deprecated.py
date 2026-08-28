import pytest


def test_deprecated():
    with pytest.warns(DeprecationWarning, match="spidermon.utils.zyte"):
        from spidermon.utils import zyte  # noqa: PLC0415

    assert zyte.Client is not None
