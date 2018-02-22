from __future__ import absolute_import
import requests
from six.moves import StringIO

from spidermon.exceptions import NotConfigured

from . import CreateReport


class CreateJobReport(CreateReport):
    api_key = None
    report_key = 'report'
    content_type = 'text/plain'

    def __init__(self, api_key=None, report_key=None, content_type=None, *args, **kwargs):
        super(CreateJobReport, self).__init__(*args, **kwargs)
        self.api_key = api_key or self.api_key
        self.report_key = report_key or self.report_key
        self.content_type = content_type or self.content_type
        if not self.api_key:
            raise NotConfigured("Missing api_key.")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(CreateJobReport, cls).from_crawler_kwargs(crawler)
        kwargs.update({
            'api_key': crawler.settings.get('SPIDERMON_JOBREPORT_APIKEY'),
            'report_key': crawler.settings.get('SPIDERMON_JOBREPORT_KEY'),
            'content_type': crawler.settings.get('SPIDERMON_JOBREPORT_CONTENTTYPE'),
        })
        return kwargs

    def after_render_report(self):
        if not self.data.job:
            raise NotConfigured('Job not available!')
        report_file = StringIO(self.report)
        self.add_job_report(
            job_key=self.data.job.key,
            key=self.report_key,
            content_type=self.content_type,
            report_file=report_file,
        )
        report_file.close()

    def add_job_report(self, job_key, key, content_type, report_file):
        r = requests.post(
            url='https://app.scrapinghub.com/api/reports/add.json',
            auth=(self.api_key, None),
            data={
                'project': str(job_key).split('/')[0],
                'key': key,
                'job': str(job_key),
                'content_type': content_type,
            },
            files={'content': report_file}
        )
