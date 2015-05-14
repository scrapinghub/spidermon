import re

from schematics.types import URLType
from schematics.transforms import EMPTY_LIST
from schematics.types.compound import ListType
from schematics.exceptions import ConversionError


def monkeypatch_urltype():
    """
    Replace schematics URL check regex with a better one (stolen from Django)
    """
    URL_REGEX = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    URLType.URL_REGEX = URL_REGEX


def monkeypatch_urltype():
    """
    Replace ListType list conversion method to avoid errors
    """
    def _force_list(self, value):
        if value is None or value == EMPTY_LIST:
            return []
        try:
            return list(value)
        except Exception, e:
            raise ConversionError('Invalid list')
    ListType._force_list = _force_list


# Apply monkeypatches
monkeypatch_urltype()
monkeypatch_urltype()