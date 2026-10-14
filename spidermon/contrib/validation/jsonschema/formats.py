from typing import Any

from jsonschema._format import (  # type: ignore[attr-defined]
    FormatChecker,
    _checks_drafts,
)

from spidermon.contrib.validation.utils import is_valid_email, is_valid_url


@_checks_drafts("url")  # type: ignore[untyped-decorator]
def is_url(instance: Any) -> bool:
    if not isinstance(instance, str):
        return True
    return is_valid_url(instance)


@_checks_drafts("email")  # type: ignore[untyped-decorator]
def is_email(instance: Any) -> bool:
    if not isinstance(instance, str):
        return True
    return is_valid_email(instance)


format_checker = FormatChecker()
