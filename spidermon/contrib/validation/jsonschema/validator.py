import re

from jsonschema.validators import extend, validator_for

from spidermon.contrib.validation.validator import Validator

from .formats import format_checker
from .translator import JSONSchemaMessageTranslator

REQUIRED_RE = re.compile("'(.+)' is a required property")


class JSONSchemaValidator(Validator):
    """Validates data against a JSON Schema.

    *types* lets you extend the set of JSON Schema types the validator
    recognizes, for values that are not natively representable in JSON, e.g.
    ``{"datetime": lambda checker, instance: isinstance(instance, arrow.Arrow)}``
    to allow ``{"type": "datetime"}`` to match ``arrow.Arrow`` instances.
    """

    default_translator = JSONSchemaMessageTranslator()
    name = "JSONSchema"

    def __init__(
        self, schema, translator=None, use_default_translator=True, types=None
    ):
        super().__init__(
            translator=translator,
            use_default_translator=use_default_translator,
        )
        self._schema = schema
        self._types = types

    def _validate(self, data, strict=False):
        validator_cls = validator_for(self._schema)
        if self._types:
            type_checker = validator_cls.TYPE_CHECKER.redefine_many(self._types)
            validator_cls = extend(validator_cls, type_checker=type_checker)
        validator = validator_cls(schema=self._schema, format_checker=format_checker)
        errors = validator.iter_errors(data)

        for error in errors:
            absolute_path = list(error.absolute_path)
            required_match = REQUIRED_RE.search(error.message)
            if required_match:
                absolute_path.append(required_match.group(1))
            field_name = ".".join([str(p) for p in absolute_path])
            self._add_errors({field_name: [error.message]})
