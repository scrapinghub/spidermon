import re

from jsonschema.validators import Draft4Validator

from .base import Validator, MessageTranslator
from . import messages


REQUIRED_RE = re.compile("'(.+)' is a required property")


class JSONSchemaMessageTranslator(MessageTranslator):
    messages = {
        re.compile("'(.+)' is a required property"):    messages.MISSING_REQUIRED_FIELD,
        re.compile("'(.+)' is too short"):              messages.FIELD_TOO_SHORT,
    }


class JSONSchemaValidator(Validator):
    default_translator = JSONSchemaMessageTranslator
    name = 'JSONSchema'

    def __init__(self, schema, translator=None, use_default_translator=True):
        super(JSONSchemaValidator, self).__init__(
            translator=translator,
            use_default_translator=use_default_translator,
        )
        self._schema = schema

    def _validate(self, data, strict=False):
        validator = Draft4Validator(self._schema)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        for e in errors:
            absolute_path = list(e.absolute_path)
            required_match = REQUIRED_RE.search(e.message)
            if required_match:
                absolute_path.append(required_match.group(1))
            field_name = '.'.join(absolute_path)
            self._add_errors({field_name: [e.message]})
