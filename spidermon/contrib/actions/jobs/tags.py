from __future__ import annotations

from typing import TYPE_CHECKING, Any

from spidermon.core.actions import Action
from spidermon.exceptions import NotConfigured

if TYPE_CHECKING:
    from scrapy.crawler import Crawler


class JobTagsAction(Action):
    tags: list[str] = []  # noqa: RUF012
    tag_settings: str | None = None

    def __init__(self, tags: str | list[str] | None = None) -> None:
        super().__init__()
        tags = tags or self.tags
        self.tags = tags if isinstance(tags, list) else [tags]

    @classmethod
    def from_crawler_kwargs(cls, crawler: Crawler) -> dict[str, Any]:
        kwargs = super().from_crawler_kwargs(crawler)
        if cls.tag_settings:
            kwargs.update({"tags": crawler.settings.get(cls.tag_settings)})
        return kwargs

    def run_action(self) -> None:
        if self.tags:
            assert self.data is not None
            if not self.data.job:
                raise NotConfigured("Job not available!")
            job_metadata = self.data.job.metadata
            job_tags = job_metadata.get("tags")
            self.process_tags(job_tags)
            job_metadata.set("tags", job_tags)

    def process_tags(self, job_metadata: list[str]) -> None:
        raise NotImplementedError


class AddJobTags(JobTagsAction):
    tag_settings = "SPIDERMON_JOB_TAGS_TO_ADD"

    def process_tags(self, job_tags: list[str]) -> None:
        tags_to_add = [tag for tag in self.tags if tag not in job_tags]
        job_tags += tags_to_add


class RemoveJobTags(JobTagsAction):
    tag_settings = "SPIDERMON_JOB_TAGS_TO_REMOVE"

    def process_tags(self, job_tags: list[str]) -> None:
        job_tags[:] = [tag for tag in job_tags if tag not in self.tags]
