from typing import Any, List, Union
from itemadapter import ItemAdapter


def traverse_nested(obj: ItemAdapter, keys: List[str]) -> ItemAdapter:
    """
    Get a nested attribute within an dictionary or ItemAdapter object.
    Raises KeyError if any of the keys in the path is not defined
    """
    current_obj = obj
    while keys:
        try:
            # Traverse next level of item object
            key = keys.pop(0)
            current_obj = ItemAdapter(current_obj[key])
        except KeyError:
            raise KeyError(f'Invalid key "{key}" for {current_obj} in {obj}')

    return current_obj


def get_nested_attribute(item: ItemAdapter, attribute_path: str):
    """
    Get the value of a nested attribute within an ItemAdapter.
    Raises KeyError if any of the keys in the path is not defined
    """
    *keys, last_key = attribute_path.split(".")
    nested_obj = traverse_nested(item, keys)
    return nested_obj.get(last_key)


def set_nested_attribute(item: ItemAdapter, attribute_path: str, value: Any):
    """
    Set the value of a nested attribute within an ItemAdapter.

    Raises KeyError if any of the keys in the path is not defined or
        if the last key in the path is not supported by its parent field
    """
    *keys, last_key = attribute_path.split(".")
    nested_obj = traverse_nested(item, keys)
    if not isinstance(nested_obj, ItemAdapter):
        nested_obj = ItemAdapter(nested_obj)

    nested_obj[last_key] = value
