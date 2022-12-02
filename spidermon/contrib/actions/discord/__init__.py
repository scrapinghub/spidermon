from __future__ import absolute_import

import logging

import requests
from spidermon.contrib.actions.templates import ActionWithTemplates
from spidermon.exceptions import NotConfigured

logger = logging.getLogger(__name__)


class DiscordMessageManager:
    sender_token = None

    def __init__(self, webhook_url, fake=False):
        if not webhook_url:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_DISCORD_WEBHOOK_URL setting."
            )
        self.webhook_url = webhook_url
        self.fake = fake

    def send_message(self, text):
        if self.fake:
            logger.info(text)
            return

        body = {"content": text}
        response = requests.post(self.webhook_url, json=body)
        response.raise_for_status()

        if not response.ok:
            logger.error(
                f"Failed to send message. Discord API error: {response.reason}"
            )


class SendDiscordMessage(ActionWithTemplates):
    webhook_url = None
    message = None
    message_template = "discord/default/message.jinja"
    fake = False

    def __init__(
        self,
        webhook_url=None,
        message=None,
        message_template=None,
        fake=None,
    ):
        super(SendDiscordMessage, self).__init__()

        self.fake = fake or self.fake
        self.manager = DiscordMessageManager(
            webhook_url or self.webhook_url, fake=self.fake
        )
        self.message = message or self.message
        self.message_template = message_template or self.message_template

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        return {
            "webhook_url": crawler.settings.get("SPIDERMON_DISCORD_WEBHOOK_URL"),
            "message": crawler.settings.get("SPIDERMON_DISCORD_MESSAGE"),
            "message_template": crawler.settings.get(
                "SPIDERMON_DISCORD_MESSAGE_TEMPLATE"
            ),
            "fake": crawler.settings.getbool("SPIDERMON_DISCORD_FAKE"),
        }

    def run_action(self):
        self.manager.send_message(self.get_message())

    def get_message(self):
        if self.message:
            return self.render_text_template(self.message)
        else:
            return self.render_template(self.message_template)
