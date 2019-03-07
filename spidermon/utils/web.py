import sys

if sys.version_info[0] == 3:
    from urllib.parse import urlparse
    from urllib.request import urlopen
else:
    from urlparse import urlparse
    from urllib import urlopen


def is_url(path):
    result = urlparse(path)
    try:
        if all([result.scheme, result.netloc, result.path]):
            return True
        return False
    except AttributeError:
        return False


def get_contents(url):
    with urlopen(url) as f:
        return f.read().decode("utf-8")
