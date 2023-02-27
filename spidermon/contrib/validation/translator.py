import re


class MessageTranslator:
    messages = {}

    def __init__(self):
        self.compiled_messages = {m: re.compile(m) for m in self.messages}

    def translate_messages(self, messages):
        return [self.translate_message(m) for m in messages]

    def translate_message(self, message):
        for target_message, pattern in self.compiled_messages.items():
            pattern_found = pattern.search(message)
            if pattern_found:
                groups = pattern_found.groupdict()
                return self.messages[target_message].format(**groups)
        return message
