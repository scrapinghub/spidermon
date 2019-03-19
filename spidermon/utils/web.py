import sys
import logging
from six.moves.urllib.parse import urlparse
from six.moves.urllib.request import urlopen


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
        logging.exception(str(e) + "\nFailed to get '{}'".format(url))
