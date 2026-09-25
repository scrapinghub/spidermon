import re
from collections.abc import Iterable
from typing import ClassVar


class MessageTranslator:
    messages: ClassVar[dict[str, str]] = {}

    def __init__(self) -> None:
        self.compiled_messages = {m: re.compile(m) for m in self.messages}

    def translate_messages(self, messages: Iterable[str]) -> list[str]:
        return [self.translate_message(m) for m in messages]

    def translate_message(self, message: str) -> str:
        for target_message, pattern in self.compiled_messages.items():
            pattern_found = pattern.search(message)
            if pattern_found:
                groups = pattern_found.groupdict()
                return self.messages[target_message].format(**groups)
        return message
