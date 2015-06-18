from spidermon.contrib.monitors.mixins import ValidationMonitorMixin, SpiderMonitorMixin

from .factory import PythonExpressionsMonitor


class ExpressionsMonitor(PythonExpressionsMonitor, ValidationMonitorMixin, SpiderMonitorMixin):
    def get_context_data(self):
        context = super(ExpressionsMonitor, self).get_context_data()
        context.update({
            'stats': self.stats,
            'validation': self.validation,
            'responses': self.responses,
        })
        return context
