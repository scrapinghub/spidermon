from __future__ import absolute_import
from cerberus import Validator as cerberus_validator
from spidermon.contrib.validation.validator import Validator


class CerberusValidator(Validator):
    default_translator = None
    name = "Cerberus"

    def __init__(self, schema, translator=None, use_default_translator=True):
        self._schema = schema
        self._translator = None

    def _validate(self, data, strict=False):
        validator = cerberus_validator(self._schema)
        validator.validate(data)
        errors = validator.errors

        for field_name, error in errors.items():
            self._add_errors({field_name: error})
