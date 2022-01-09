"""
Module to hold a singleton Scrapinghub client.
"""
import os

from scrapinghub import ScrapinghubClient

from .hubstorage import _Hubstorage


class Client(_Hubstorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._spider_name = os.environ.get("SHUB_SPIDER")

    @property
    def client(self):
        if self._client is None:
            self._client = ScrapinghubClient()
        return self._client

    @property
    def spider(self):
        if not self._spider:
            self._spider = self.project.spiders.get(self._spider_name)
        return self._project


client = Client()
