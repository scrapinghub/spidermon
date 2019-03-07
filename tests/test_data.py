from __future__ import absolute_import
import pytest

from spidermon.data import Data
from spidermon.exceptions import InvalidDataOperation


@pytest.fixture
def data():
    return Data(item_scraped_count=150)


def test_attribute_access(data):
    assert data["item_scraped_count"] == 150


def test_dictionary_access(data):
    assert data.item_scraped_count == 150


def test_attribute_set(data):
    with pytest.raises(InvalidDataOperation):
        data.item_scraped_count = "some value"


def test_dictionary_set(data):
    with pytest.raises(InvalidDataOperation):
        data["item_scraped_count"] = "some value"


def test_delete(data):
    with pytest.raises(InvalidDataOperation):
        del data["item_scraped_count"]


def test_pop(data):
    with pytest.raises(InvalidDataOperation):
        data.pop("item_scraped_count", None)


def test_clear(data):
    with pytest.raises(InvalidDataOperation):
        data.clear()


def test_update(data):
    with pytest.raises(InvalidDataOperation):
        data.update({"item_scraped_count": 0})


def test_setdefault(data):
    with pytest.raises(InvalidDataOperation):
        data.setdefault("another_value", 0)
