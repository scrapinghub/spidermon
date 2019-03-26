from __future__ import absolute_import
from spidermon.contrib.validation.translator import MessageTranslator
from spidermon.contrib.validation import messages


class JSONSchemaMessageTranslator(MessageTranslator):
    messages = {
        r"^.+ is a required property$": messages.MISSING_REQUIRED_FIELD,
        r"^.+ is not of type u?'array'$": messages.INVALID_ARRAY,
        r"^.+ is not of type u?'boolean'$": messages.INVALID_BOOLEAN,
        r"^.+ is not of type u?'integer'$": messages.INVALID_INT,
        r"^.+ is not of type u?'number'$": messages.INVALID_NUMBER,
        r"^.+ is not of type u?'object'$": messages.INVALID_OBJECT,
        r"^.+ is not of type u?'string'$": messages.INVALID_STRING,
        r"^.+ is not of type u?'null'$": messages.NOT_NULL,
        r"^.+ is not valid under any of the given schemas$": messages.NOT_VALID_UNDER_ANY_SCHEMA,
        r"^.+ is valid under each of .+$": messages.VALID_FOR_SEVERAL_EXCLUSIVE_SCHEMAS,
        r"^Additional items are not allowed .*$": messages.TOO_MANY_ITEMS,
        r"^Additional properties are not allowed (?P<unexpected_fields>.*)$": messages.UNEXPECTED_FIELDS,
        r"^.+ is a dependency of .+$": messages.MISSING_DEPENDENT_FIELD,
        r"^.* is not one of .+$": messages.VALUE_NOT_IN_CHOICES,
        r"^.* is not a 'date-time'$": messages.INVALID_DATETIME,
        r"^.* is not a 'email'$": messages.INVALID_EMAIL,
        r"^.* is not a 'ipv4'$": messages.INVALID_IPV4,
        r"^.* is not a 'ipv6'$": messages.INVALID_IPV6,
        r"^.* is not a 'hostname'$": messages.INVALID_HOSTNAME,
        r"^.* is not a 'url'$": messages.INVALID_URL,
        r"^.* is not a 'uri'$": messages.INVALID_URI,
        r"^.* is not a 'regex'$": messages.INVALID_REGEX,
        r"^.* is not a 'color'$": messages.INVALID_COLOR,
        r"^.* has too many properties$": messages.TOO_MANY_PROPERTIES,
        r"^.* does not have enough properties": messages.NOT_ENOUGH_PROPERTIES,
        r"^.* is greater than the maximum of .*$": messages.NUMBER_TOO_HIGH,
        r"^.* is greater than or equal to the maximum of .*$": messages.NUMBER_TOO_HIGH,
        r"^.* is less than the minimum of .*$": messages.NUMBER_TOO_LOW,
        r"^.* is less than or equal to the minimum of .*$": messages.NUMBER_TOO_LOW,
        r"^.* is not a multiple of .*$": messages.NOT_MULTIPLE_OF,
        r"^.* is not allowed for .*$": messages.NOT_ALLOWED_VALUE,
        r"^.+ is too short$": messages.FIELD_TOO_SHORT,
        r"^.+ is too long$": messages.FIELD_TOO_LONG,
        r"^.+ does not match .*$": messages.REGEX_NOT_MATCHED,
        r"^.+ has non-unique elements$": messages.NOT_UNIQUE,
    }
