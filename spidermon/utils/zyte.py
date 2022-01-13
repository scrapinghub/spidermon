"""
Module to hold a singleton to Zyte's Scrapy Cloud client.

It expects that "SHUB_JOBKEY" be present as environment variable, as
well as either "SH_APIKEY" or "SHUB_JOBAUTH" to access Scrapy Cloud API.
"""
import os

try:
    from scrapinghub import ScrapinghubClient

    HAS_CLIENT = True
except ImportError:
    HAS_CLIENT = False


class Client:
    def __init__(self):
        self.available = HAS_CLIENT and "SHUB_JOBKEY" in os.environ
        self._client = None
        self._project = None
        self._spider = None
        self._job = None
        if self.available:
            self.job_key = os.environ["SHUB_JOBKEY"]
            self.project_id, self.spider_id, self.job_id = map(
                int, self.job_key.split("/")
            )
        else:
            self.project_id = None
            self.spider_id = None
            self.job_id = None

    @property
    def client(self):
        if not self._client:
            self._client = ScrapinghubClient()
        return self._client

    @property
    def project(self):
        if not self._project:
            self._project = self.client.get_project(str(self.project_id))
        return self._project

    @property
    def spider(self):
        if not self._spider:
            spider_name = self.job.metadata.get("spider")
            self._spider = self.project.spiders.get(spider_name)
        return self._spider

    @property
    def job(self):
        if not self._job:
            self._job = self.client.get_job(self.job_key)
        return self._job

    def close(self):
        if self._client:
            self._client.close()


client = Client()
