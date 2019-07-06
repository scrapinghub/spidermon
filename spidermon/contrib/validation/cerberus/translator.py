from __future__ import absolute_import
from spidermon.contrib.validation.translator import MessageTranslator
from spidermon.contrib.validation import messages


class CerberusMessageTranslator(MessageTranslator):
    messages = {
        r"must be of integer type": messages.INVALID_INT,
        r"must be of number type": messages.INVALID_NUMBER,
        r"must be of float type": messages.INVALID_FLOAT,
        r"must be of string type": messages.INVALID_STRING,
        r"required field":messages.MISSING_REQUIRED_FIELD,
        r"value does not match regex.*$":messages.REGEX_NOT_MATCHED,
        r"unallowed values.*$":messages.NOT_ALLOWED_VALUE,
        r"Unexpected field.*$":messages.UNEXPECTED_FIELD,
        # r"":messages.,
    }
