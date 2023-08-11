import os

try:
    from scrapinghub import ScrapinghubClient

    HAS_CLIENT = True
except ImportError:
    HAS_CLIENT = False


class Client:
    """
    Wrapper over ScrapinghubClient that indicates with its available
    attribute if it can be used to fetch data from Scrapy Cloud API.

    It expects that "SHUB_JOBKEY" be present as environment variable.
    Also, it will look up for Scrapy Cloud API key in `SHUB_APIKEY` Scrapy
    setting, then for the environment variables `SH_APIKEY` and `SHUB_JOBAUTH`.
    Note that "SHUB_JOBAUTH" can't access all API endpoints.
    """

    def __init__(self, settings):
        self.available = HAS_CLIENT and "SHUB_JOBKEY" in os.environ
        self._client = None
        self._project = None
        self._spider = None
        self._job = None
        self._settings = settings
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
            self._client = ScrapinghubClient(self._apikey())
        return self._client

    def _apikey(self):
        apikey = (
            self._settings.get("SHUB_APIKEY")
            or os.environ.get("SH_APIKEY")
            or os.environ.get("SHUB_JOBAUTH")
        )
        if not apikey:
            raise RuntimeError(
                "No Scrapy Cloud API key found. Please set `SHUB_APIKEY` in Scrapy settings,"
                " or either `SH_APIKEY` or `SHUB_JOBAUTH` environment variables `."
            )
        return apikey

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
