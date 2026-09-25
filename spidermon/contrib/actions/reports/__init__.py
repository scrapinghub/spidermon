from __future__ import annotations

from typing import TYPE_CHECKING, Any

from spidermon.contrib.actions.templates import ActionWithTemplates
from spidermon.exceptions import NotConfigured

if TYPE_CHECKING:
    from scrapy.crawler import Crawler


class CreateReport(ActionWithTemplates):
    template = None

    def __init__(
        self,
        template: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.template = template or self.template
        self.report = ""
        if not self.template:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_REPORT_TEMPLATE setting.",
            )

    @classmethod
    def from_crawler_kwargs(cls, crawler: Crawler) -> dict[str, Any]:
        kwargs = super().from_crawler_kwargs(crawler)
        kwargs.update(
            {
                "template": crawler.settings.get("SPIDERMON_REPORT_TEMPLATE"),
                "context": crawler.settings.getdict("SPIDERMON_REPORT_CONTEXT"),
            },
        )
        return kwargs

    def run_action(self) -> None:
        self.before_render_report()
        self.render_report()
        self.after_render_report()

    def before_render_report(self) -> None:
        pass

    def render_report(self) -> None:
        assert self.template is not None
        self.report = self.render_template(self.template)

    def after_render_report(self) -> None:
        pass
