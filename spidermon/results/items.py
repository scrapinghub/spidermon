from __future__ import absolute_import
from spidermon import settings


class ItemResult(object):
    def __init__(self, item):
        self.item = item
        self.status = settings.UNDEFINED_STATUS
        self.error = None
        self.reason = None
        self.id = id(self)


class MonitorResult(ItemResult):
    name = "monitor"

    def __init__(self, item):
        super(MonitorResult, self).__init__(item)
        self.status = settings.MONITOR.STATUSES.DEFAULT

    @property
    def monitor(self):
        return self.item


class ActionResult(ItemResult):
    name = "action"

    def __init__(self, item):
        super(ActionResult, self).__init__(item)
        self.status = settings.ACTION.STATUSES.DEFAULT

    @property
    def action(self):
        return self.item
