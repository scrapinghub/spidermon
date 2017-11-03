from __future__ import absolute_import
from jsonschema._format import FormatChecker, _draft_checkers
from jsonschema.compat import str_types

from spidermon.contrib.validation.utils import is_valid_url, is_valid_email
from six import iterkeys


def is_url(instance):
    if not isinstance(instance, str_types):
        return True
    return is_valid_url(instance)


def is_email(instance):
    if not isinstance(instance, str_types):
        return True
    return is_valid_email(instance)


_spidermon_checkers = {
    'url': (is_url, ()),
    'email': (is_email, ()),
}

#_draft4_checkers = ['email', 'ipv4', 'ipv6', 'hostname', 'uri', 'date-time', 'regex']

for format_name, (func, raises) in _spidermon_checkers.items():
    FormatChecker.cls_checks(format_name, raises)(func)


format_checker = FormatChecker(_draft_checkers["draft4"] + list(iterkeys(_spidermon_checkers)))
