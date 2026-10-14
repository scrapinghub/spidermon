from __future__ import annotations

from typing import TYPE_CHECKING, Any

from spidermon.exceptions import NotConfigured

if TYPE_CHECKING:
    from collections.abc import Iterable


class Context(dict[str, Any]):
    """
    Stores context for python expressions.

    Also keeps track of not configured components (variables) of the context
    to throw NotConfigured exception in the right time, when test is
    evaluated by interpreter, instead of throwing it in building-context time
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._notconfigured: list[str] = []

    def __getitem__(self, item: Any) -> Any:
        if item in self._notconfigured:
            raise NotConfigured(f"{item} not available!")
        return super().__getitem__(item)

    def extend_via_attrs(self, obj: object, attrs: Iterable[str]) -> None:
        """Extend context with names of object attributes and their values."""
        for attr in attrs:
            try:
                super().__setitem__(attr, getattr(obj, attr))
            except NotConfigured:  # noqa: PERF203
                self._notconfigured.append(attr)
