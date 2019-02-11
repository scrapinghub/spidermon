from __future__ import absolute_import
from spidermon.contrib.validation.translator import MessageTranslator
from spidermon.contrib.validation import messages


class SchematicsMessageTranslator(MessageTranslator):
    messages = {
        r"^Rogue field$": messages.UNEXPECTED_FIELD,
        # BaseType
        r"^This field is required.$": messages.MISSING_REQUIRED_FIELD,
        r"^Value must be one of .*\.$": messages.VALUE_NOT_IN_CHOICES,
        # StringType
        r"^Couldn't interpret '.*' as string\.$": messages.INVALID_STRING,
        r"^String value is too long\.$": messages.FIELD_TOO_LONG,
        r"^String value is too short\.$": messages.FIELD_TOO_SHORT,
        r"^String value did not match validation regex\.$": messages.REGEX_NOT_MATCHED,
        # DateTimeType
        r"^Could not parse .+\. Should be ISO ?8601(?: or timestamp)?\.$": messages.INVALID_DATETIME,
        r"^Could not parse .+\. Valid formats: .+$": messages.INVALID_DATETIME,
        # DateType
        r"^Could not parse .+\. Should be ISO ?8601 \(YYYY-MM-DD\)\.$": messages.INVALID_DATE,
        # NumberType
        r"^.+ value should be greater than .+$": messages.NUMBER_TOO_LOW,
        r"^.+ value should be less than .+$": messages.NUMBER_TOO_HIGH,
        # IntType
        r"^Value '.*' is not int\.?$": messages.INVALID_INT,
        # FloatType
        r"^Value '.*' is not float\.?$": messages.INVALID_FLOAT,
        # LongType
        r"^Value '.*' is not long\.?$": messages.INVALID_LONG,
        # Decimalype
        r"^Number '.*' failed to convert to a decimal\.?$": messages.INVALID_DECIMAL,
        r"^Value '.*' is not decimal\.?$": messages.INVALID_DECIMAL,
        r"^Value should be greater than .+$": messages.NUMBER_TOO_LOW,
        r"^Value should be less than .+$": messages.NUMBER_TOO_HIGH,
        # BooleanType
        r"^Must be either true or false\.$": messages.INVALID_BOOLEAN,
        # EmailType
        r"^Not a well[ -]formed email address\.$": messages.INVALID_EMAIL,
        # URLType
        r"^Not a well[ -]formed URL\.$": messages.INVALID_URL,
        # UUIDType
        r"^Couldn't interpret '.*' value as UUID\.$": messages.INVALID_UUID,
        # IPv4Type
        r"^Invalid IPv4 address$": messages.INVALID_IPV4,
        # HashType
        r"^Hash value is wrong length\.$": messages.INVALID_HASH_LENGTH,
        r"^Hash value is not hexadecimal\.$": messages.INVALID_HASH,
        # ListType
        r"^Invalid list$": messages.INVALID_LIST,
        r"^Could not interpret the value as a list$": messages.INVALID_LIST,
        r"^Please provide at least \d+ items?\.$": messages.LIST_TOO_SHORT,
        r"^Please provide no more than \d+ items?\.$": messages.LIST_TOO_LONG,
        # DictType
        r"^Only (?:dictionaries|mappings) may be used in a DictType$": messages.INVALID_DICT,
        # DictType
        r"^Please use a mapping for this field or .+ "
        r"instance instead of .*\.$": messages.INVALID_CHILD_CONTENT,
    }
