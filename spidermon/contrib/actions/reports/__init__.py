from __future__ import absolute_import
from spidermon.contrib.actions.templates import ActionWithTemplates
from spidermon.exceptions import NotConfigured


class CreateReport(ActionWithTemplates):
    template = None

    def __init__(self, template=None, *args, **kwargs):
        super(CreateReport, self).__init__(*args, **kwargs)
        self.template = template or self.template
        self.report = ""
        if not self.template:
            raise NotConfigured("You must define one template file.")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(CreateReport, cls).from_crawler_kwargs(crawler)
        kwargs.update(
            {
                "template": crawler.settings.get("SPIDERMON_REPORT_TEMPLATE"),
                "context": crawler.settings.getdict("SPIDERMON_REPORT_CONTEXT"),
            }
        )
        return kwargs

    def run_action(self):
        self.before_render_report()
        self.render_report()
        self.after_render_report()

    def before_render_report(self):
        pass

    def render_report(self):
        self.report = self.render_template(self.template)

    def after_render_report(self):
        pass
