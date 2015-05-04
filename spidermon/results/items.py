from spidermon import settings


class ItemResult(object):
    def __init__(self, item):
        self.item = item
        self.status = settings.UNDEFINED_STATUS
        self.error = None
        self.reason = None


class TestResult(ItemResult):
    name = 'test'

    @property
    def test(self):
        return self.item


class ActionResult(ItemResult):
    name = 'action'

    @property
    def action(self):
        return self.item