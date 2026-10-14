from typing import Any, NoReturn

from .exceptions import InvalidDataOperation


class Data(dict[str, Any]):
    """Read-only dict whose keys can also be read as attributes, e.g.
    ``data.stats`` for ``data["stats"]``."""

    def __getattr__(self, name: str) -> Any:
        if name in self:
            return self[name]
        raise AttributeError(f"Key '{name}' not found.")

    def _immutable(self, *args: Any, **kws: Any) -> NoReturn:
        raise InvalidDataOperation(
            "Immutable Data! You cannot add or modify read-only data.",
        )

    update = _immutable
    setdefault = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    __setitem__ = _immutable
    __delitem__ = _immutable
    __setattr__ = _immutable
