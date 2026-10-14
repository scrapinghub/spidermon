from __future__ import annotations

import abc
from typing import Any

from spidermon import settings


class OptionsMetaclassBase(abc.ABCMeta):
    __options_class__: type[OptionsBase] | None = None
    options: OptionsBase

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, Any],
    ) -> OptionsMetaclassBase:
        cls = super().__new__(mcs, name, bases, attrs)
        if not cls.__options_class__:
            raise TypeError(
                "Options class not defined! are you trying to use OptionsMetaclassBase?",
            )
        cls.options = cls.__options_class__()
        return cls


class OptionsBase:
    __options_name__ = "options"

    @classmethod
    def add_or_create(cls, target: object) -> bool:
        if not hasattr(target, cls.__options_name__):
            setattr(target, cls.__options_name__, cls())
            return True
        return False

    def _get_attributes(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def __str__(self) -> str:
        return "<{name}:({attributes})>".format(
            name=self.__class__.__name__,
            attributes=", ".join(
                f"{attr}={getattr(self, attr)}" for attr in self._get_attributes()
            ),
        )


class MonitorOptions(OptionsBase):
    def __init__(self) -> None:
        self.name: str | None = settings.MONITOR.DEFAULT_NAME
        self.description: str = settings.MONITOR.DEFAULT_DESCRIPTION
        self.level: int | None = None
        self.meta: dict[str, Any] = {}
        self.order: int = settings.MONITOR.DEFAULT_ORDER


class MonitorOptionsMetaclass(OptionsMetaclassBase):
    __options_class__ = MonitorOptions


class ActionOptions(OptionsBase):
    def __init__(self) -> None:
        self.name: str | None = None
        self.description: str = settings.ACTION.DEFAULT_DESCRIPTION


class ActionOptionsMetaclass(OptionsMetaclassBase):
    __options_class__ = ActionOptions
