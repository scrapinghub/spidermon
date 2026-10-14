import json
import logging
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import urlopen

from scrapy.utils.misc import load_object

logger = logging.getLogger(__name__)


def get_schema_from(source: str) -> Any:
    if is_schema_url(source):
        schema = get_contents(source)
        try:
            return json.loads(schema)  # type: ignore[arg-type]
        except Exception:
            logger.exception(f"Could not parse schema from '{source}'")
    elif source.endswith(".json"):
        with Path(source).open() as f:
            try:
                return json.load(f)
            except Exception:
                logger.exception(f"Could not parse schema in '{source}'")
    else:
        schema = load_object(source)
        if isinstance(schema, str):
            return json.loads(schema)
        return schema


def is_schema_url(path: str) -> bool:
    result = urlparse(path)
    try:
        return all([result.scheme, result.netloc, result.path])
    except AttributeError:
        return False


def get_contents(url: str) -> str | None:
    try:
        with urlopen(url) as f:  # noqa: S310
            contents: str = f.read().decode("utf-8")
            return contents
    except Exception:
        logger.exception(f"Failed to get '{url}'")
        return None
