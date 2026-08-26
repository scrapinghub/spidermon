from unittest.mock import MagicMock

import pytest

from spidermon.contrib.zyte.monitors.mixins.job import JobMonitorMixin
from spidermon.exceptions import NotConfigured


def test_job_not_available():
    mixin = JobMonitorMixin()
    mixin.data = MagicMock(job=None)
    with pytest.raises(NotConfigured):
        mixin.job  # noqa: B018


def test_job_available():
    mixin = JobMonitorMixin()
    mixin.data = MagicMock()
    assert mixin.job is mixin.data.job
