from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

try:
    from scrapinghub import ScrapinghubClient

    HAS_CLIENT = True
except ImportError:
    HAS_CLIENT = False

if TYPE_CHECKING:
    from scrapy.settings import BaseSettings


class Client:
    """
    Wrapper over ScrapinghubClient that indicates with its available
    attribute if it can be used to fetch data from Scrapy Cloud API.

    It expects that "SHUB_JOBKEY" be present as environment variable.
    Also, it will look up for Scrapy Cloud API key in `SHUB_APIKEY` Scrapy
    setting, then for the environment variables `SH_APIKEY` and `SHUB_JOBAUTH`.
    Note that "SHUB_JOBAUTH" can't access all API endpoints.
    """

    def __init__(self, settings: BaseSettings) -> None:
        self.available = HAS_CLIENT and "SHUB_JOBKEY" in os.environ
        self._client: ScrapinghubClient | None = None
        self._project: Any = None
        self._spider: Any = None
        self._job: Any = None
        self.project_id: int | None
        self.spider_id: int | None
        self.job_id: int | None
        self._settings = settings
        if self.available:
            self.job_key = os.environ["SHUB_JOBKEY"]
            self.project_id, self.spider_id, self.job_id = map(
                int,
                self.job_key.split("/"),
            )
        else:
            self.project_id = None
            self.spider_id = None
            self.job_id = None

    @property
    def client(self) -> ScrapinghubClient:
        if not self._client:
            self._client = ScrapinghubClient(self._apikey())
        return self._client

    def _apikey(self) -> str:
        apikey = (
            self._settings.get("SHUB_APIKEY")
            or os.environ.get("SH_APIKEY")
            or os.environ.get("SHUB_JOBAUTH")
        )
        if not apikey:
            raise RuntimeError(
                "No Scrapy Cloud API key found. Please set `SHUB_APIKEY` in Scrapy settings,"
                " or either `SH_APIKEY` or `SHUB_JOBAUTH` environment variables `.",
            )
        return apikey

    @property
    def project(self) -> Any:
        if not self._project:
            self._project = self.client.get_project(str(self.project_id))
        return self._project

    @property
    def spider(self) -> Any:
        if not self._spider:
            spider_name = self.job.metadata.get("spider")
            self._spider = self.project.spiders.get(spider_name)
        return self._spider

    @property
    def job(self) -> Any:
        if not self._job:
            self._job = self.client.get_job(self.job_key)
        return self._job

    def close(self) -> None:
        if self._client:
            self._client.close()
