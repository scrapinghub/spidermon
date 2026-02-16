try:
    import scrapy
except ImportError:
    pass
else:
    import importlib.metadata
    from packaging.version import Version

    SCRAPY_VERSION = Version(importlib.metadata.version("Scrapy"))