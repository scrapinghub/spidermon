from spidermon.core.actions import Action


class AddJobTags(Action):
    tags = []

    def __init__(self, tags=None):
        super(AddJobTags, self).__init__()
        tags = tags or self.tags
        self.tags = tags if isinstance(tags, list) else [tags]

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        return {
            'tags': crawler.settings.get('SPIDERMON_JOB_TAGS'),
        }

    def run_action(self):
        if self.data.hubstorage.available and self.tags:
            job_metadata = self.data.hubstorage.job.metadata
            for tag in self.tags:
                if tag not in job_metadata['tags']:
                    job_metadata['tags'].append(tag)
            job_metadata.save()