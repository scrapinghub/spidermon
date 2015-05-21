from spidermon.exceptions import NotConfigured

from . import GenerateReport


class GenerateFileReport(GenerateReport):
    template = None
    filename = None

    def __init__(self, template, filename, context=None):
        super(GenerateFileReport, self).__init__(template=template, context=context)
        self.filename = filename or self.filename
        if not self.filename:
            raise NotConfigured("You must define a template output file.")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(GenerateFileReport, cls).from_crawler_kwargs(crawler)
        kwargs.update({
            'filename': crawler.settings.get('SPIDERMON_REPORT_FILENAME'),
        })
        return kwargs

    def after_render_report(self):
        with open(self.filename, "w") as f:
            f.write(self.report)