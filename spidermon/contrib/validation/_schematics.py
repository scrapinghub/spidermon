import re

from schematics.exceptions import ModelValidationError, ModelConversionError
from schematics.types import URLType

from .base import Validator, MessageTranslator
from . import messages


class SchematicsMessageTranslator(MessageTranslator):
    messages = {
        'Rogue field':                          messages.UNEXPECTED_FIELD,
        'This field is required.':              messages.MISSING_REQUIRED_FIELD,
        'String value is too long.':            messages.FIELD_TOO_LONG,
        'String value is too short.':            messages.FIELD_TOO_SHORT,
        'Not a well formed email address.':     'Invalid email',
        'Not a well formed URL.':               'Invalid URL',
    }


class SchematicsValidator(Validator):
    default_translator = SchematicsMessageTranslator
    name = 'Schematics'

    def __init__(self, model, translator=None, use_default_translator=True):
        super(SchematicsValidator, self).__init__(
            translator=translator,
            use_default_translator=use_default_translator,
        )
        self._model = model
        self._fields_required = {}
        self._save_required_fields()
        self._data = {}

    def _validate(self, data, strict=False):
        self._set_data(data)
        model = self._get_model_instance(strict=strict)
        try:
            model.validate()
        except ModelValidationError, e:
            self._add_errors(e.messages)
        self._restore_required_fields()

    def _reset(self):
        super(SchematicsValidator, self)._reset()
        self._data = {}

    def _set_data(self, data):
        self._data = dict(data)

    def _get_model_instance(self, strict):
        try:
            return self._model(raw_data=self._data, strict=strict)
        except ModelConversionError, e:
            self._add_errors(e.messages)
            for field_name in self._errors.keys():
                self._set_field_as_not_required(field_name)
                self._data.pop(field_name)
            return self._model(raw_data=self._data, strict=strict)

    def _save_required_fields(self):
        for field_name, field in self._model._fields.items():
            self._fields_required[field_name] = field.required

    def _restore_required_fields(self):
        for field_name, required in self._fields_required.items():
            self._model._fields[field_name].required = required

    def _set_field_as_not_required(self, field_name):
        if field_name in self._model._fields:
            self._model._fields[field_name].required = False

    def _add_errors(self, errors):
        for field_name, messages in errors.items():
            self._errors[field_name] += messages if isinstance(messages, list) else [messages]


# TO-DO: Comment
# Monkeypatches
# URL REGEX: Stolen for django
URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|' # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
URLType.URL_REGEX = URL_REGEX
