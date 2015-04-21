import pytest

from spidermon.stats import Stats
from spidermon.exceptions import InvalidStatsOperation


@pytest.fixture
def stats():
    return Stats({
        'a': 1,
        'b': 2,
    })


def test_attribute_access(stats):
    assert(stats['a'] == 1)
    assert(stats['b'] == 2)


def test_dictionary_access(stats):
    assert(stats.a == 1)
    assert(stats.b == 2)


def test_attribute_set(stats):
    with pytest.raises(InvalidStatsOperation):
        stats.a = 'some value'


def test_dictionary_set(stats):
    with pytest.raises(InvalidStatsOperation):
        stats['a'] = 'some value'


def test_delete(stats):
    with pytest.raises(InvalidStatsOperation):
        del stats['a']


def test_pop(stats):
    with pytest.raises(InvalidStatsOperation):
        stats.pop('a', None)
