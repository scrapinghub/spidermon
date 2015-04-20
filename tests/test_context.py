import pytest


from spidermon.stats import Stats
from spidermon.context import Context, create_context, create_context_dict


@pytest.fixture
def stats():
    return Stats({
        'a': 1,
        'b': 2,
    })


def check_stats(stats):
    assert isinstance(stats, Stats)
    assert stats.a == 1
    assert stats.b == 2


def test_create_context(stats):
    context = create_context(stats)
    assert isinstance(context, Context)
    check_stats(context.stats)


def test_create_context_dict(stats):
    context_dict = create_context_dict(stats)
    assert isinstance(context_dict, dict)
    check_stats(context_dict['stats'])
