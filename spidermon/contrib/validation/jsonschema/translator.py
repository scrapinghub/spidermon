from spidermon.contrib.validation.translator import MessageTranslator
from spidermon.contrib.validation import messages


class JSONSchemaMessageTranslator(MessageTranslator):
    messages = {
        r".+ is a required property":    messages.MISSING_REQUIRED_FIELD,
        r".+ is not of type u?'number'":   messages.INVALID_NUMBER,
        #r".+ is not of type 'string'":   messages.INVALID_STRING,
        r".+ is not of type u?'object'":   messages.INVALID_OBJECT,
        r".+ is too short":              messages.FIELD_TOO_SHORT,
    }

