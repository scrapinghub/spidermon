from __future__ import annotations

import copy
import json
import warnings
from collections import OrderedDict
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scrapy.crawler import Crawler
    from scrapy.settings import BaseSettings


def getdictorlist(
    crawler: Crawler,
    name: str,
    default: Any = None,
) -> dict[Any, Any] | list[Any]:
    value = crawler.settings.get(name, default)
    if value is None:
        return {}
    if isinstance(value, str):
        try:
            loaded: dict[Any, Any] | list[Any] = json.loads(
                value, object_pairs_hook=OrderedDict
            )
        except ValueError:
            return value.split(",")
        return loaded
    copied: dict[Any, Any] | list[Any] = copy.deepcopy(value)
    return copied


def get_aws_credentials(settings: BaseSettings) -> tuple[str | None, str | None]:
    aws_access_key_id = settings.get("SPIDERMON_AWS_ACCESS_KEY")
    aws_secret_access_key = settings.get("SPIDERMON_AWS_SECRET_KEY")

    if aws_access_key_id and aws_secret_access_key:
        warnings.warn(
            "SPIDERMON_AWS_ACCESS_KEY and SPIDERMON_AWS_SECRET_KEY are deprecated. "
            "Please update them to SPIDERMON_AWS_ACCESS_KEY_ID and SPIDERMON_AWS_SECRET_ACCESS_KEY. "
            "Scrapy settings AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are also valid.",
            DeprecationWarning,
            stacklevel=2,
        )

    if not aws_access_key_id and not aws_secret_access_key:
        aws_access_key_id = settings.get("SPIDERMON_AWS_ACCESS_KEY_ID")
        aws_secret_access_key = settings.get("SPIDERMON_AWS_SECRET_ACCESS_KEY")

    if not aws_access_key_id and not aws_secret_access_key:
        aws_access_key_id = settings.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = settings.get("AWS_SECRET_ACCESS_KEY")

    return (aws_access_key_id, aws_secret_access_key)
