from spidermon.contrib.monitors.mixins import ValidationMonitorMixin

from .factory import PythonExpressionsMonitor


class ExpressionsMonitor(PythonExpressionsMonitor, ValidationMonitorMixin):
    def get_context_data(self):
        context = super(ExpressionsMonitor, self).get_context_data()
        context.update({
            'stats': self.stats,
            'validation': self.validation,
        })
        return context
