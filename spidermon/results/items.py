from typing import Any

from spidermon import settings


class ItemResult:
    name: str

    def __init__(self, item: Any) -> None:
        self.item = item
        self.status = settings.UNDEFINED_STATUS
        self.error: str | None = None
        self.reason: str | None = None
        self.id = id(self)


class MonitorResult(ItemResult):
    name = "monitor"

    def __init__(self, item: Any) -> None:
        super().__init__(item)
        self.status = settings.MONITOR.STATUSES.DEFAULT

    @property
    def monitor(self) -> Any:
        return self.item


class ActionResult(ItemResult):
    name = "action"

    def __init__(self, item: Any) -> None:
        super().__init__(item)
        self.status = settings.ACTION.STATUSES.DEFAULT

    @property
    def action(self) -> Any:
        return self.item
