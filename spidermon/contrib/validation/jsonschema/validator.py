from __future__ import absolute_import
import re

from jsonschema.validators import validators as jsonschema_validators

from spidermon.contrib.validation.validator import Validator

from .translator import JSONSchemaMessageTranslator
from .formats import format_checker


REQUIRED_RE = re.compile("'(.+)' is a required property")


class JSONSchemaValidator(Validator):
    default_translator = JSONSchemaMessageTranslator()
    default_jsonschema_version = 'draft4'
    name = 'JSONSchema'

    def __init__(self, schema, version='draft4', translator=None, use_default_translator=True):
        super(JSONSchemaValidator, self).__init__(
            translator=translator,
            use_default_translator=use_default_translator,
        )
        self._schema = schema
        self._version = version

    def _validate(self, data, strict=False):
        default_validator = jsonschema_validators.get(self.default_jsonschema_version)

        validator_cls = jsonschema_validators.get(self._version)
        if validator_cls is None:
            validator_cls = default_validator

        validator = validator_cls(
            schema=self._schema,
            format_checker=format_checker,
        )
        errors = validator.iter_errors(data)

        for error in errors:
            absolute_path = list(error.absolute_path)
            required_match = REQUIRED_RE.search(error.message)
            if required_match:
                absolute_path.append(required_match.group(1))
            field_name = '.'.join([str(p) for p in absolute_path])
            self._add_errors({field_name: [error.message]})
