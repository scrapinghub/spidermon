from spidermon.contrib.actions.templates import ActionWithTemplates
from spidermon.exceptions import NotConfigured


class BaseReport(ActionWithTemplates):
    template = None

    def __init__(self, template):
        super(BaseReport, self).__init__()
        self.template = template or self.template
        self.report = ''
        if not self.template:
            raise NotConfigured("You must define one template file.")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        return {
            'template': crawler.settings.get('SPIDERMON_REPORT_TEMPLATE'),
        }

    def run_action(self):
        self.render_report()
        print self.report

    def render_report(self):
        self.report = self.render_template(self.template)
