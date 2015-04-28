import pytest

from spidermon.stats import Stats
from spidermon.exceptions import InvalidStatsOperation

from fixtures.stats import *

@pytest.fixture
def stats():
    return Stats(STATS_A)


def test_attribute_access(stats):
    assert(stats['item_scraped_count'] == 150)


def test_dictionary_access(stats):
    assert(stats.item_scraped_count == 150)


def test_attribute_set(stats):
    with pytest.raises(InvalidStatsOperation):
        stats.item_scraped_count = 'some value'


def test_dictionary_set(stats):
    with pytest.raises(InvalidStatsOperation):
        stats['item_scraped_count'] = 'some value'


def test_delete(stats):
    with pytest.raises(InvalidStatsOperation):
        del stats['item_scraped_count']


def test_pop(stats):
    with pytest.raises(InvalidStatsOperation):
        stats.pop('item_scraped_count', None)
