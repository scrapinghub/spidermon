from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Protocol, TypeVar, cast

if TYPE_CHECKING:
    from collections.abc import Callable

    from spidermon.core.options import OptionsBase

_T = TypeVar("_T")


class _Decorator(Protocol):
    def __call__(self, fn: _T, /) -> _T: ...


class DecoratorWithAttributes:
    name: str | None = None
    attributes: ClassVar[dict[str, _Decorator]] = {}

    def __init__(self) -> None:
        if not self.name:
            raise AttributeError("No name defined!")
        if not self.attributes:
            raise AttributeError("No attributes defined!")

    def __getattr__(self, name: str) -> _Decorator:
        if name not in self.attributes:
            raise AttributeError(
                "Invalid {attribute} '{name}', allowed values: {values}".format(
                    attribute=self.name,
                    name=name,
                    values=", ".join([f"'{attr}'" for attr in self.attributes]),
                ),
            )
        return self.attributes[name]


class OptionsDecorator:
    @classmethod
    def set_value(
        cls,
        options_class: type[OptionsBase],
        value_name: str,
    ) -> Callable[[Any], Callable[[_T], _T]]:
        def value_decorator(value: Any) -> Callable[[_T], _T]:
            def decorator(fn: _T) -> _T:
                options_class.add_or_create(fn)
                setattr(cast("Any", fn).options, value_name, value)
                return fn

            return decorator

        return value_decorator

    @classmethod
    def set_fixed_value(
        cls,
        options_class: type[OptionsBase],
        value_name: str,
        value: Any,
    ) -> Callable[[_T], _T]:
        def decorator(fn: _T) -> _T:
            options_class.add_or_create(fn)
            setattr(cast("Any", fn).options, value_name, value)
            return fn

        return decorator
