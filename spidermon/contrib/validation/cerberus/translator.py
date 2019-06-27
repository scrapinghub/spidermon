from __future__ import absolute_import
from spidermon.contrib.validation.translator import MessageTranslator
from spidermon.contrib.validation import messages


class CerberusMessageTranslator(MessageTranslator):
    messages = {
        r"must be of integer type": messages.INVALID_INT,
    }
