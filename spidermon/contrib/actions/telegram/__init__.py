from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

import requests

from spidermon.contrib.actions.templates import ActionWithTemplates
from spidermon.exceptions import NotConfigured

if TYPE_CHECKING:
    from scrapy.crawler import Crawler

logger = logging.getLogger(__name__)


class SimplyTelegramClient:
    send_message_api = "https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={text}"

    def __init__(self, token: str) -> None:
        self.token = token

    def send_message(self, message: str, recipient: str) -> None:
        api_url = self.send_message_api.format(
            token=self.token,
            chat_id=recipient,
            text=message,
        )
        r = requests.get(api_url, timeout=60).json()
        if r.get("ok") is False:
            logger.error(
                "Failed to send message. Telegram api error: %s",
                json.dumps(r),
            )


class TelegramMessageManager:
    sender_token = None

    def __init__(self, sender_token: str | None = None, fake: bool = False) -> None:
        sender_token = sender_token or self.sender_token
        if not sender_token:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_TELEGRAM_SENDER_TOKEN setting.",
            )

        self.fake = fake
        self._client = SimplyTelegramClient(sender_token)

    def send_message(self, to: list[str], text: str) -> None:
        if self.fake:
            logger.info(text)
            return
        for recipient in to:
            self._client.send_message(text, recipient)


class SendTelegramMessage(ActionWithTemplates):
    message = None
    message_template = "telegram/default/message.jinja"
    recipients = None
    sender_token = None
    fake = False

    def __init__(
        self,
        sender_token: str | None = None,
        recipients: list[str] | None = None,
        message: str | None = None,
        message_template: str | None = None,
        fake: bool | None = None,
    ) -> None:
        super().__init__()

        self.fake = fake or self.fake
        self.manager = TelegramMessageManager(
            sender_token=sender_token or self.sender_token,
            fake=self.fake,
        )

        self.recipients = recipients or self.recipients
        self.message = message or self.message
        self.message_template = message_template or self.message_template
        if not self.recipients:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_TELEGRAM_RECIPIENTS setting.",
            )

    @classmethod
    def from_crawler_kwargs(cls, crawler: Crawler) -> dict[str, Any]:
        return {
            "sender_token": crawler.settings.get("SPIDERMON_TELEGRAM_SENDER_TOKEN"),
            "recipients": crawler.settings.getlist("SPIDERMON_TELEGRAM_RECIPIENTS"),
            "message": crawler.settings.get("SPIDERMON_TELEGRAM_MESSAGE"),
            "message_template": crawler.settings.get(
                "SPIDERMON_TELEGRAM_MESSAGE_TEMPLATE",
            ),
            "fake": crawler.settings.getbool("SPIDERMON_TELEGRAM_FAKE"),
        }

    def run_action(self) -> None:
        assert self.recipients is not None
        self.manager.send_message(to=self.recipients, text=self.get_message())

    def get_message(self) -> str:
        if self.message:
            return self.render_text_template(self.message)
        return self.render_template(self.message_template)
