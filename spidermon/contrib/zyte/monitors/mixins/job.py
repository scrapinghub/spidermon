from spidermon.exceptions import NotConfigured


class JobMonitorMixin:
    @property
    def job(self):
        if not self.data.job:
            raise NotConfigured("Job not available!")
        return self.data.job
