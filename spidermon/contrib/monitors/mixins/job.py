from spidermon.exceptions import NotConfigured


class JobMonitorMixin(object):
    @property
    def job(self):
        if 'job' not in self.data:
            raise NotConfigured('Job not available!')
        return self.data.job
