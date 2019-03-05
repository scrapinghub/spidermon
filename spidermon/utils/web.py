from urllib.parse import urlparse
from urllib.request import urlopen


def is_url(path: str) -> bool:
    result = urlparse(path)
    try:
        if all([result.schema, result.netloc, result.path]):
            return True
        return False
    except AttributeError:
        return False


def get_contents(url: str) -> str:
    with urlopen(url) as f:
        return f.read().decode("utf-8")
