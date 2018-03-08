from __future__ import absolute_import
import re


class MessageTranslator(object):
    messages = {}

    def __init__(self):
        self.compiled_messages = dict([(m, re.compile(m)) for m in self.messages])

    def translate_messages(self, messages):
        return [self.translate_message(m) for m in messages]

    def translate_message(self, message):
        for target_message, pattern in self.compiled_messages.items():
            if pattern.search(message):
                return self.messages[target_message]  # TO-DO: Add substitution?
        return message

