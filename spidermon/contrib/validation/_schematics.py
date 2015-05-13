import re

from schematics.exceptions import ModelValidationError, ModelConversionError, ConversionError
from schematics.types import URLType
from schematics.transforms import EMPTY_LIST
from schematics.types.compound import ListType

from .base import Validator, MessageTranslator
from . import messages as m


class SchematicsMessageTranslator(MessageTranslator):
    messages = {
        r"^Rogue field$":                                               m.UNEXPECTED_FIELD,

        # BaseType
        r"^This field is required.$":                                   m.MISSING_REQUIRED_FIELD,
        r"^Value must be one of .*\.$":                                 m.VALUE_NOT_IN_CHOICES,

        # StringType
        r"^Couldn't interpret '.*' as string\.$":                       m.INVALID_STRING,
        r"^String value is too long\.$":                                m.FIELD_TOO_LONG,
        r"^String value is too short\.$":                               m.FIELD_TOO_SHORT,
        r"^String value did not match validation regex\.$":             m.REGEX_NOT_MATCHED,

        # DateTimeType
        r"^Could not parse .+\. Should be ISO8601\.$":                  m.INVALID_DATETIME,

        # DateType
        r"^Could not parse .+\. Should be ISO8601 \(YYYY-MM-DD\)\.$":   m.INVALID_DATE,

        # NumberType
        "^.+ value should be greater than .+$":                         m.NUMBER_TOO_LOW,
        "^.+ value should be less than .+$":                            m.NUMBER_TOO_HIGH,

        # IntType
        r"^Value '.*' is not int$":                                     m.INVALID_INT,

        # FloatType
        r"^Value '.*' is not float$":                                   m.INVALID_FLOAT,

        # LongType
        r"^Value '.*' is not long$":                                    m.INVALID_LONG,

        # Decimalype
        r"^Number '.*' failed to convert to a decimal$":                m.INVALID_DECIMAL,
        r"^Value should be greater than .+$":                           m.NUMBER_TOO_LOW,
        r"^Value should be less than .+$":                              m.NUMBER_TOO_HIGH,

        # BooleanType
        r'^Must be either true or false\.$':                            m.INVALID_BOOLEAN,

        # EmailType
        r"^Not a well formed email address\.$":                         m.INVALID_EMAIL,

        # URLType
        r"^Not a well formed URL\.$":                                   m.INVALID_URL,

        # UUIDType
        "^Couldn't interpret '.*' value as UUID\.$":                    m.INVALID_UUID,

        # IPv4Type
        r"^Invalid IPv4 address$":                                      m.INVALID_IPV4,

        # HashType
        r"^Hash value is wrong length\.$":                              m.INVALID_HASH_LENGTH,
        r"^Hash value is not hexadecimal\.$":                           m.INVALID_HASH,

        # ListType
        r"^Invalid list$":                                              m.INVALID_LIST,
        r"^Please provide at least \d+ items?\.$":                      m.LIST_TOO_SHORT,
        r"^Please provide no more than \d+ items?\.$":                  m.LIST_TOO_LONG,

        # DictType
        r"^Only dictionaries may be used in a DictType$":               m.INVALID_DICT,

        # DictType
        r"^Please use a mapping for this field or .+ "
        r"instance instead of .*\.$":                                   m.INVALID_CHILD_CONTENT,
    }


class SchematicsValidator(Validator):
    default_translator = SchematicsMessageTranslator()
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
            for field_name in e.messages.keys():
                self._set_field_as_not_required(field_name)
                self._data.pop(field_name)
            return self._get_model_instance(strict=strict)

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
            if isinstance(messages, dict):
                transformed_errors = self._get_transformed_child_errors(field_name, messages)
                self._add_errors(transformed_errors)
            else:
                self._errors[field_name] += messages if isinstance(messages, list) else [messages]

    def _get_transformed_child_errors(self, field_name, errors):
        return dict([('%s.%s' % (field_name, k), v) for k, v in errors.items()])


# ----------------------------------
# Monkeypatches
# ----------------------------------
# Replace schematics URL check regex with a better one (stolen from Django)
URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|' # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
URLType.URL_REGEX = URL_REGEX


# Replace ListType list conversion method to avoid errors
def _force_list(self, value):
    if value is None or value == EMPTY_LIST:
        return []
    try:
        return list(value)
    except Exception, e:
        raise ConversionError('Invalid list')
ListType._force_list = _force_list