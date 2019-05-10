import logging

import json
from scrapy.utils.misc import load_object
import six
from six.moves.urllib.parse import urlparse
from six.moves.urllib.request import urlopen

logger = logging.getLogger(__name__)


def get_schema_from(source):
    if is_schema_url(source):
        schema = get_contents(source)
        try:
            return json.loads(schema)
        except Exception as e:
            logger.exception(
                str(e) + "\nCould not parse schema from '{}'".format(source)
            )
    elif source.endswith(".json"):
        with open(source, "r") as f:
            try:
                return json.load(f)
            except Exception as e:
                logger.exception(
                    str(e) + "\nCould not parse schema in '{}'".format(source)
                )
    else:
        schema = load_object(source)
        if isinstance(schema, six.string_types):
            return json.loads(schema)
        return schema


def is_schema_url(path):
    result = urlparse(path)
    try:
        return all([result.scheme, result.netloc, result.path])
    except AttributeError:
        return False


def get_contents(url):
    try:
        with urlopen(url) as f:
            return f.read().decode("utf-8")
    except Exception as e:
        logger.exception(str(e) + "\nFailed to get '{}'".format(url))
