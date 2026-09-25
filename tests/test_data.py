import pytest

from spidermon.data import Data
from spidermon.exceptions import InvalidDataOperation


@pytest.fixture
def data() -> Data:
    return Data(item_scraped_count=150)


def test_attribute_access(data: Data) -> None:
    assert data["item_scraped_count"] == 150


def test_dictionary_access(data: Data) -> None:
    assert data.item_scraped_count == 150


def test_attribute_set(data: Data) -> None:
    with pytest.raises(InvalidDataOperation):
        data.item_scraped_count = "some value"  # type: ignore[attr-defined]


def test_dictionary_set(data: Data) -> None:
    with pytest.raises(InvalidDataOperation):
        data["item_scraped_count"] = "some value"


def test_delete(data: Data) -> None:
    with pytest.raises(InvalidDataOperation):
        del data["item_scraped_count"]


def test_pop(data: Data) -> None:
    with pytest.raises(InvalidDataOperation):
        data.pop("item_scraped_count", None)


def test_clear(data: Data) -> None:
    with pytest.raises(InvalidDataOperation):
        data.clear()


def test_update(data: Data) -> None:
    with pytest.raises(InvalidDataOperation):
        data.update({"item_scraped_count": 0})


def test_setdefault(data: Data) -> None:
    with pytest.raises(InvalidDataOperation):
        data.setdefault("another_value", 0)
