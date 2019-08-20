from __future__ import absolute_import

import six
if six.PY2:
    from collections import Mapping
else:
    from collections.abc import Mapping

from cerberus.validator import (
    Validator as cerberus_validator,
    DocumentError,
    SchemaError,
)
from spidermon.contrib.validation.validator import Validator
from .translator import CerberusMessageTranslator


class CerberusValidator(Validator):
    default_translator = CerberusMessageTranslator()
    name = "Cerberus"

    def __init__(self, schema, translator=None, use_default_translator=True):
        super(CerberusValidator, self).__init__(
            translator=translator, use_default_translator=use_default_translator
        )
        if isinstance(schema, Mapping):
            self._schema = schema
        else:
            raise SchemaError("Validation schema missing")

    def _validate(self, data, strict=False):
        if data is None:
            raise DocumentError("Data is missing")

        try:
            validator = cerberus_validator(self._schema)
            validator.validate(data)
        except SchemaError:
            raise ValueError(
                "{} is not of the right format, must be mapping".format(self._schema)
            )
        except DocumentError:
            raise ValueError(
                "{} is not of the right format, must be mapping".format(data)
            )
        for field_name, error in validator.errors.items():
            self._add_errors({field_name: error})
