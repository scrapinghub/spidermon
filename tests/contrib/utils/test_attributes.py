from dataclasses import dataclass

import pytest

pytest.importorskip("itemadapter")

from itemadapter import ItemAdapter

from spidermon.contrib.utils.attributes import (
    get_nested_attribute,
    set_nested_attribute,
)


def test_get_nested_attribute():
    item = ItemAdapter({"foo": "bar", "attr1": {"attr2": {"attr3": "foobar"}}})

    assert get_nested_attribute(item, "foo") == "bar"
    assert get_nested_attribute(item, "attr1.attr2.attr3") == "foobar"
    assert get_nested_attribute(item, "missing_attribute") is None

    # Missing intermiddle attribute
    with pytest.raises(KeyError):
        get_nested_attribute(item, "attr1.missing_attribute.attr2")

    # Intermiddle attribute is None
    item = ItemAdapter({"foo": None})
    with pytest.raises(KeyError):
        get_nested_attribute(item, "foo.missing_attribute")


def test_set_nested_attribute():
    item = ItemAdapter({"foo": None, "attr1": {"attr2": {"attr3": None}}})
    set_nested_attribute(item, "foo", "foobar")
    assert item["foo"] == "foobar"

    set_nested_attribute(item, "attr1.attr2.attr3", "bar")
    assert get_nested_attribute(item, "attr1.attr2.attr3") == "bar"

    # Set undefined attribute when underlaying class allows it
    set_nested_attribute(item, "missing_attribute", "foo")
    assert item["missing_attribute"] == "foo"

    # Set undefined attribute when underlaying class doesn't allow it
    @dataclass
    class NestedField:
        foo: str

    @dataclass
    class DummyItem:
        attr1: NestedField

    item = ItemAdapter(DummyItem(attr1=NestedField(foo="bar")))
    with pytest.raises(
        KeyError, match="NestedField does not support field: missing_attribute"
    ):
        set_nested_attribute(item, "attr1.missing_attribute", "foo")
