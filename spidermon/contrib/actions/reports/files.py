from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from spidermon.exceptions import NotConfigured

from . import CreateReport

if TYPE_CHECKING:
    from scrapy.crawler import Crawler


class CreateFileReport(CreateReport):
    filename = None

    def __init__(self, filename: str | None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.filename = filename or self.filename
        if not self.filename:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_REPORT_FILENAME setting.",
            )

    @classmethod
    def from_crawler_kwargs(cls, crawler: Crawler) -> dict[str, Any]:
        kwargs = super().from_crawler_kwargs(crawler)
        kwargs.update({"filename": crawler.settings.get("SPIDERMON_REPORT_FILENAME")})
        return kwargs

    def after_render_report(self) -> None:
        assert self.filename is not None
        rendered_filename = self.render_text_template(self.filename)

        with Path(rendered_filename).open("w", encoding="utf-8") as f:
            f.write(self.report)
