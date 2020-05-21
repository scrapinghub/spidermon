"""
Module to hold a reference to singleton Hubstorage client and Job instance
"""
from __future__ import absolute_import
import os
from codecs import decode

from six.moves import map

try:
    try:
        from scrapinghub import HubstorageClient
    except ImportError:
        from hubstorage.client import HubstorageClient
except ImportError:
    HubstorageClient = None


class _Hubstorage(object):
    def __init__(self):
        self.available = "SHUB_JOBKEY" in os.environ and HubstorageClient is not None
        self._client = None
        self._project = None
        self._job = None
        if self.available:
            self.job_key = os.environ["SHUB_JOBKEY"]
            self._project_id, self._spider_id, self._job_id = map(
                int, self.job_key.split("/")
            )
        else:
            self._project_id = None
            self._spider_id = None
            self._job_id = None

    @property
    def auth(self):
        return decode(os.environ["SHUB_JOBAUTH"], "hex_codec").decode("utf-8")

    @property
    def endpoint(self):
        return os.environ.get("SHUB_STORAGE")

    @property
    def project_id(self):
        return self._project_id

    @property
    def spider_id(self):
        return self._spider_id

    @property
    def job_id(self):
        return self._job_id

    @property
    def client(self):
        if self._client is None:
            self._client = HubstorageClient(endpoint=self.endpoint, auth=self.auth)
        return self._client

    @property
    def project(self):
        if self._project is None:
            self._project = self.client.get_project(str(self.project_id))
        return self._project

    @property
    def job(self):
        if self._job is None:
            self._job = self.project.get_job((self.spider_id, self.job_id))
        return self._job

    def close(self):
        if self._client is not None:
            self._client.close()


hs = _Hubstorage()
