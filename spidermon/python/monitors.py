from __future__ import absolute_import
from spidermon.contrib.monitors.mixins import ValidationMonitorMixin, SpiderMonitorMixin

from .factory import PythonExpressionsMonitor
from .context import Context


class ExpressionsMonitor(
    PythonExpressionsMonitor, ValidationMonitorMixin, SpiderMonitorMixin
):
    def get_context_data(self):
        context = Context()
        attrs = ["stats", "crawler", "spider", "job", "validation", "responses"]
        context.extend_via_attrs(self, attrs)
        return context
