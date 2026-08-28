import pytest

pytest.importorskip("scrapy")


def test_deprecated():
    with pytest.warns(DeprecationWarning, match="spidermon.contrib.actions.jobs.tags"):
        from spidermon.contrib.actions.jobs import tags  # noqa: PLC0415

    assert tags.JobTagsAction is not None
