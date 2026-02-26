from spidermon.contrib.monitors.mixins import SpiderMonitorMixin, ValidationMonitorMixin

from .context import Context
from .factory import PythonExpressionsMonitor


class ExpressionsMonitor(
    PythonExpressionsMonitor,
    ValidationMonitorMixin,
    SpiderMonitorMixin,
):
    def get_context_data(self):
        context = Context()
        attrs = ["stats", "crawler", "spider", "job", "validation", "responses"]
        context.extend_via_attrs(self, attrs)
        return context
