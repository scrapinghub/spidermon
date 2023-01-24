from jsonschema._format import FormatChecker, _checks_drafts

from spidermon.contrib.validation.utils import is_valid_url, is_valid_email


@_checks_drafts("url")
def is_url(instance):
    if not isinstance(instance, str):
        return True
    return is_valid_url(instance)


@_checks_drafts("email")
def is_email(instance):
    if not isinstance(instance, str):
        return True
    return is_valid_email(instance)


format_checker = FormatChecker()
