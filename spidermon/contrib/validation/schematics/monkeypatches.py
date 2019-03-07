from __future__ import absolute_import
import schematics


def monkeypatch_urltype():
    """
    Replace schematics URL check regex with a better one (stolen from Django).

    This patch cannot be applied to Schematics 2.* because the URL validation
    is more complex.
    """
    from schematics.types import URLType
    from spidermon.contrib.validation.utils import URL_REGEX

    URLType.URL_REGEX = URL_REGEX


def monkeypatch_listtype():
    """
    Replace ListType list conversion method to avoid errors
    """
    from schematics.transforms import EMPTY_LIST
    from schematics.types.compound import ListType
    from schematics.exceptions import ConversionError

    def _force_list(self, value):
        if value is None or value == EMPTY_LIST:
            return []
        try:
            return list(value)
        except Exception as e:
            raise ConversionError("Invalid list")

    ListType._force_list = _force_list


# Apply monkeypatches
if schematics.__version__.startswith("1."):
    monkeypatch_urltype()
    monkeypatch_listtype()
