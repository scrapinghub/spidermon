import copy
import json
from collections import OrderedDict

import six


def getdictorlist(crawler, name, default=None):
    value = crawler.settings.get(name, default)
    if value is None:
        return {}
    if isinstance(value, six.string_types):
        try:
            return json.loads(value, object_pairs_hook=OrderedDict)
        except ValueError:
            return value.split(",")
    return copy.deepcopy(value)
