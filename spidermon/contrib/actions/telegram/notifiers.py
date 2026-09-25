from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import SendTelegramMessage

if TYPE_CHECKING:
    from scrapy.crawler import Crawler


class SendTelegramMessageSpiderStarted(SendTelegramMessage):
    message_template = "telegram/spider/notifier/start/message.jinja"


class SendTelegramMessageSpiderFinished(SendTelegramMessage):
    message_template = "telegram/spider/notifier/finish/message.jinja"
    include_ok_messages = False
    include_error_messages = True

    def __init__(
        self,
        include_ok_messages: bool | None = None,
        include_error_messages: bool | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.include_ok_messages = include_ok_messages or self.include_ok_messages
        self.include_error_messages = (
            include_error_messages or self.include_error_messages
        )

    @classmethod
    def from_crawler_kwargs(cls, crawler: Crawler) -> dict[str, Any]:
        kwargs = super().from_crawler_kwargs(crawler)
        kwargs.update(
            {
                "include_ok_messages": crawler.settings.get(
                    "SPIDERMON_TELEGRAM_NOTIFIER_INCLUDE_OK_MESSAGES",
                ),
                "include_error_messages": crawler.settings.get(
                    "SPIDERMON_TELEGRAM_NOTIFIER_INCLUDE_ERROR_MESSAGES",
                ),
            },
        )
        return kwargs

    def get_template_context(self) -> dict[str, Any]:
        context = super().get_template_context()
        context.update(
            {
                "include_ok_messages": self.include_ok_messages,
                "include_error_messages": self.include_error_messages,
            },
        )
        return context


class SendTelegramMessageSpiderRunning(SendTelegramMessageSpiderFinished):
    message_template = "telegram/spider/notifier/periodic/message.jinja"
