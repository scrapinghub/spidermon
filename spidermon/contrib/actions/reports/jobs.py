import requests
import StringIO

from spidermon.exceptions import NotConfigured

from . import GenerateReport


class GenerateJobReport(GenerateReport):
    template = None
    api_key = None
    report_key = 'report'
    content_type = 'text/plain'

    def __init__(self, template, api_key=None, report_key=None, content_type=None):
        super(GenerateJobReport, self).__init__(template=template)
        self.api_key = api_key or self.api_key
        self.report_key = report_key or self.report_key
        self.content_type = content_type or self.content_type
        if not self.api_key:
            raise NotConfigured("Missing api_key.")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(GenerateJobReport, cls).from_crawler_kwargs(crawler)
        kwargs.update({
            'api_key': crawler.settings.get('SPIDERMON_JOBREPORT_APIKEY'),
            'report_key': crawler.settings.get('SPIDERMON_JOBREPORT_KEY'),
            'content_type': crawler.settings.get('SPIDERMON_JOBREPORT_CONTENTTYPE'),
        })
        return kwargs

    def after_render_report(self):
        if self.data.hubstorage.available:
            report_file = StringIO.StringIO(self.report)
            self.add_job_report(
                auth=self.data.hubstorage.auth,
                job_key=self.data.hubstorage.job_key,
                key=self.report_key,
                content_type=self.content_type,
                report_file=report_file,
            )
            report_file.close()

    def add_job_report(self, auth, job_key, key, content_type, report_file):
        r = requests.post(
            url='https://dash.scrapinghub.com/api/reports/add.json',
            auth=(self.api_key, None),
            data={
                'project': str(job_key).split('/')[0],
                'key': key,
                'job': str(job_key),
                'content_type': content_type,
            },
            files = {'content': report_file}
        )
