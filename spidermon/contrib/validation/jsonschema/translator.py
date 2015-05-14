from spidermon.contrib.validation.translator import MessageTranslator
from spidermon.contrib.validation import messages


class JSONSchemaMessageTranslator(MessageTranslator):
    messages = {
        r"^.+ is a required property$":                         messages.MISSING_REQUIRED_FIELD,

        r"^.+ is not of type u?'array'$":                       messages.INVALID_ARRAY,
        r"^.+ is not of type u?'boolean'$":                     messages.INVALID_BOOLEAN,
        r"^.+ is not of type u?'integer'$":                     messages.INVALID_INT,
        r"^.+ is not of type u?'number'$":                      messages.INVALID_NUMBER,
        r"^.+ is not of type u?'object'$":                      messages.INVALID_OBJECT,
        r"^.+ is not of type u?'string'$":                      messages.INVALID_STRING,
        r"^.+ is not of type u?'null'$":                        messages.NOT_NULL,

        r"^.+ is not valid under any of the given schemas$":    messages.NOT_VALID_UNDER_ANY_SCHEMA,
        r"^.+ is valid under each of .+$":                      messages.VALID_FOR_SEVERAL_EXCLUSIVE_SCHEMAS,

        #r".+ is not of type u?'number'":   messages.INVALID_NUMBER,
        #r".+ is not of type 'string'":   messages.INVALID_STRING,
        #r".+ is not of type u?'object'":   messages.INVALID_OBJECT,
        r"^.+ is too short$":              messages.FIELD_TOO_SHORT,
        r"^.+ is too long$":              messages.FIELD_TOO_LONG,


        #r".+ is not a 'url'":              messages.INVALID_URL,
    }

