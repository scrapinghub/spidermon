import pytest

from spidermon.stats import Stats
from spidermon.context import Context, create_context, create_context_dict

from fixtures.stats import *


@pytest.fixture
def stats():
    return Stats(STATS_A)


def check_stats(stats):
    assert isinstance(stats, Stats)
    assert stats.item_scraped_count == 150


def test_create_context(stats):
    context = create_context(stats)
    assert isinstance(context, Context)
    check_stats(context.stats)


def test_create_context_dict(stats):
    context_dict = create_context_dict(stats)
    assert isinstance(context_dict, dict)
    check_stats(context_dict['stats'])
