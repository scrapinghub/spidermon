import copy
import json
from collections import OrderedDict
import warnings

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


def get_aws_credentials(settings):
    aws_access_key_id = settings.get("SPIDERMON_AWS_ACCESS_KEY")
    aws_secret_access_key = settings.get("SPIDERMON_AWS_SECRET_KEY")

    if aws_access_key_id and aws_secret_access_key:
        warnings.warn(
            "SPIDERMON_AWS_ACCESS_KEY and SPIDERMON_AWS_SECRET_KEY are deprecated. "
            "Please update them to SPIDERMON_AWS_ACCESS_KEY_ID and SPIDERMON_AWS_SECRET_ACCESS_KEY. "  # noqa
            "Scrapy settings AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are also valid.",
            DeprecationWarning,
        )

    if not aws_access_key_id and not aws_secret_access_key:
        aws_access_key_id = settings.get("SPIDERMON_AWS_ACCESS_KEY_ID")
        aws_secret_access_key = settings.get("SPIDERMON_AWS_SECRET_ACCESS_KEY")

    if not aws_access_key_id and not aws_secret_access_key:
        aws_access_key_id = settings.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = settings.get("AWS_SECRET_ACCESS_KEY")

    return (aws_access_key_id, aws_secret_access_key)
