from __future__ import absolute_import
from spidermon.core.actions import Action
from spidermon.exceptions import NotConfigured


class JobTagsAction(Action):
    tags = []
    tag_settings = None

    def __init__(self, tags=None):
        super(JobTagsAction, self).__init__()
        tags = tags or self.tags
        self.tags = tags if isinstance(tags, list) else [tags]

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(JobTagsAction, cls).from_crawler_kwargs(crawler)
        if cls.tag_settings:
            kwargs.update({"tags": crawler.settings.get(cls.tag_settings)})
        return kwargs

    def run_action(self):
        if self.tags:
            if not self.data.job:
                raise NotConfigured("Job not available!")
            job_metadata = self.data.job.metadata
            self.process_tags(job_metadata)
            job_metadata.save()

    def process_tags(self, job_metadata):
        raise NotImplementedError


class AddJobTags(JobTagsAction):
    tag_settings = "SPIDERMON_JOB_TAGS_TO_ADD"

    def process_tags(self, job_metadata):
        for tag in self.tags:
            if tag not in job_metadata["tags"]:
                job_metadata["tags"].append(tag)


class RemoveJobTags(JobTagsAction):
    tag_settings = "SPIDERMON_JOB_TAGS_TO_REMOVE"

    def process_tags(self, job_metadata):
        for tag in self.tags:
            if tag in job_metadata["tags"]:
                job_metadata["tags"].remove(tag)
