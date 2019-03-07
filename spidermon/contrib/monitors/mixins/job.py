from __future__ import absolute_import
from spidermon.exceptions import NotConfigured


class JobMonitorMixin(object):
    @property
    def job(self):
        if not self.data.job:
            raise NotConfigured("Job not available!")
        return self.data.job
