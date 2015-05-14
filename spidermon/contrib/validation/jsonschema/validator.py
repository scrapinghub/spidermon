from __future__ import absolute_import
import re

from jsonschema.validators import Draft4Validator

from spidermon.contrib.validation.validator import Validator

from .translator import JSONSchemaMessageTranslator


REQUIRED_RE = re.compile("'(.+)' is a required property")


class JSONSchemaValidator(Validator):
    default_translator = JSONSchemaMessageTranslator()
    name = 'JSONSchema'

    def __init__(self, schema, translator=None, use_default_translator=True):
        super(JSONSchemaValidator, self).__init__(
            translator=translator,
            use_default_translator=use_default_translator,
        )
        self._schema = schema

    def _validate(self, data, strict=False):
        validator = Draft4Validator(
            schema=self._schema,
            #format_checker=format_checker,
        )
        errors = validator.iter_errors(data)
        for e in errors:
            #print e
            absolute_path = list(e.absolute_path)
            required_match = REQUIRED_RE.search(e.message)
            if required_match:
                absolute_path.append(required_match.group(1))
            field_name = '.'.join(absolute_path)
            self._add_errors({field_name: [e.message]})
