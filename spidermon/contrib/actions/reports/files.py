from __future__ import absolute_import
from spidermon.exceptions import NotConfigured

from . import CreateReport


class CreateFileReport(CreateReport):
    filename = None

    def __init__(self, filename, *args, **kwargs):
        super(CreateFileReport, self).__init__(*args, **kwargs)
        self.filename = filename or self.filename
        if not self.filename:
            raise NotConfigured("You must define a template output file.")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(CreateFileReport, cls).from_crawler_kwargs(crawler)
        kwargs.update({"filename": crawler.settings.get("SPIDERMON_REPORT_FILENAME")})
        return kwargs

    def after_render_report(self):
        rendered_filename = self.render_text_template(self.filename)

        with open(rendered_filename, "w") as f:
            f.write(self.report)
