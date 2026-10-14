from __future__ import annotations

import re
from collections import defaultdict
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .translator import MessageTranslator

RE_PATTERN_INSTANCE = type(re.compile(""))


class Validator:
    default_translator: MessageTranslator | None = None
    name = "validator"

    def __init__(
        self,
        translator: MessageTranslator | None = None,
        use_default_translator: bool = True,
    ) -> None:
        self._errors: defaultdict[str, list[str]] = defaultdict(list)
        if not translator and use_default_translator and self.default_translator:
            translator = self.default_translator
        self._translator = translator

    def validate(
        self, data: Any, strict: bool = True
    ) -> tuple[bool, dict[str, list[str]]]:
        self._reset()
        self._validate(data, strict=strict)
        return not self.has_errors, self.errors

    def _reset(self) -> None:
        self._errors = defaultdict(list)

    def _validate(self, data: Any, strict: bool = True) -> None:
        raise NotImplementedError

    @property
    def has_errors(self) -> bool:
        return len(self._errors) > 0

    @property
    def errors(self) -> dict[str, list[str]]:
        if not self._translator:
            return self._errors
        return {
            field_name: self._translator.translate_messages(messages)
            for field_name, messages in self._errors.items()
        }

    def _add_errors(self, errors: Mapping[str, str | list[str]]) -> None:
        for field_name, messages in errors.items():
            self._errors[field_name] += (
                messages if isinstance(messages, list) else [messages]
            )
