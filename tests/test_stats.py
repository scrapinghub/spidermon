import pytest


from spidermon.stats import Stats
from spidermon.exceptions import InvalidOperation


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
    with pytest.raises(InvalidOperation):
        stats.a = 'some value'


def test_dictionary_set(stats):
    with pytest.raises(InvalidOperation):
        stats['a'] = 'some value'


def test_delete(stats):
    with pytest.raises(InvalidOperation):
        del stats['a']


def test_pop(stats):
    with pytest.raises(InvalidOperation):
        stats.pop('a', None)
