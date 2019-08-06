from __future__ import absolute_import
import re
import logging
import json
import six
from six.moves.urllib.parse import urlparse
from six.moves.urllib.request import urlopen
from scrapy.utils.misc import load_object

logger = logging.getLogger(__name__)

URL_REGEX = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)

EMAIL_REGEX = re.compile(
    # dot-atom
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
    # quoted-string
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016' r'-\177])*"'
    # domain
    r")@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,32}\.?$",
    re.IGNORECASE,
)


def is_valid_url(url):
    return not URL_REGEX.match(url) is None


def is_valid_email(email):
    return not EMAIL_REGEX.match(email) is None

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
