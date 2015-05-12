import re
from collections import defaultdict


RE_PATTERN_INSTANCE = type(re.compile(''))


class Validator(object):
    default_translator = None
    name = 'validator'

    def __init__(self, translator=None, use_default_translator=True):
        self._errors = defaultdict(list)
        if not translator and use_default_translator and self.default_translator:
            translator = self.default_translator
        self._translator = translator

    def validate(self, data, strict=True):
        self._reset()
        self._validate(data, strict=strict)
        return not self.has_errors, self.errors

    def _reset(self):
        self._errors = defaultdict(list)

    def _validate(self, data, strict=True):
        raise NotImplementedError

    @property
    def has_errors(self):
        return len(self._errors) > 0

    @property
    def errors(self):
        if not self._translator:
            return self._errors
        else:
            return dict([(field_name, self._translator.translate_messages(messages))
                         for field_name, messages in self._errors.items()])

    def _add_errors(self, errors):
        for field_name, messages in errors.items():
            self._errors[field_name] += messages if isinstance(messages, list) else [messages]


class MessageTranslator(object):
    messages = {}

    @classmethod
    def translate_messages(cls, messages):
        return [cls.translate_message(m) for m in messages]

    @classmethod
    def translate_message(cls, message):
        for target_message in cls.messages:
            if isinstance(target_message, RE_PATTERN_INSTANCE) and target_message.search(message):
                return cls.messages[target_message]  # TO-DO: Add substitution?
            elif message == target_message:
                return cls.messages[target_message]
        return message

