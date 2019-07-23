from __future__ import absolute_import
from spidermon.contrib.validation.translator import MessageTranslator
from spidermon.contrib.validation import messages


class CerberusMessageTranslator(MessageTranslator):
    messages = {
        r"^must be of integer type$": messages.INVALID_INT,
        r"^must be of number type$": messages.INVALID_NUMBER,
        r"^must be of float type$": messages.INVALID_FLOAT,
        r"^must be of string type$": messages.INVALID_STRING,
        r"^required field$":messages.MISSING_REQUIRED_FIELD,
        r"^value does not match regex.*$":messages.REGEX_NOT_MATCHED,
        r"^unallowed values.*$":messages.NOT_ALLOWED_VALUE,
        r"^Unknown field.*$":messages.UNKNOWN_FIELD,
        r"^null value not allowed$":messages.NULL_NOT_ALLOWED,
        r"^must be of list type$":messages.INVALID_LIST,
        r"^must be of boolean type$":messages.INVALID_BOOLEAN,
        r"^must be of binary type$":messages.INVALID_BINARY,
        r"^must be of set type$":messages.INVALID_SET,
        r"^must be of dict type$":messages.INVALID_DICT,
        r"^must be of date type$":messages.INVALID_DATE,
        r"^must be of datetime type$":messages.INVALID_DATETIME,
        r"^empty values not allowed$":messages.EMPTY_NOT_ALLOWED,


    }
