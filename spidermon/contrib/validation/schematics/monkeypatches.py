from schematics.types import URLType
from schematics.transforms import EMPTY_LIST
from schematics.types.compound import ListType
from schematics.exceptions import ConversionError

from spidermon.contrib.validation.utils import URL_REGEX


def monkeypatch_urltype():
    """
    Replace schematics URL check regex with a better one (stolen from Django)
    """
    URLType.URL_REGEX = URL_REGEX


def monkeypatch_listtype():
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
monkeypatch_listtype()