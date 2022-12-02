from __future__ import absolute_import

from . import SendDiscordMessage


class SendDiscordMessageSpiderStarted(SendDiscordMessage):
    message_template = "discord/spider/notifier/start/message.jinja"


class SendDiscordMessageSpiderFinished(SendDiscordMessage):
    message_template = "discord/spider/notifier/finish/message.jinja"
    include_ok_messages = False
    include_error_messages = True

    def __init__(
        self, include_ok_messages=None, include_error_messages=None, *args, **kwargs
    ):
        super(SendDiscordMessageSpiderFinished, self).__init__(*args, **kwargs)
        self.include_ok_messages = include_ok_messages or self.include_ok_messages
        self.include_error_messages = (
            include_error_messages or self.include_error_messages
        )

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(SendDiscordMessageSpiderFinished, cls).from_crawler_kwargs(
            crawler
        )
        kwargs.update(
            {
                "include_ok_messages": crawler.settings.get(
                    "SPIDERMON_DISCORD_NOTIFIER_INCLUDE_OK_MESSAGES"
                ),
                "include_error_messages": crawler.settings.get(
                    "SPIDERMON_DISCORD_NOTIFIER_INCLUDE_ERROR_MESSAGES"
                ),
            }
        )
        return kwargs

    def get_template_context(self):
        context = super(SendDiscordMessageSpiderFinished, self).get_template_context()
        context.update(
            {
                "include_ok_messages": self.include_ok_messages,
                "include_error_messages": self.include_error_messages,
            }
        )
        return context


class SendDiscordMessageSpiderRunning(SendDiscordMessageSpiderFinished):
    message_template = "discord/spider/notifier/periodic/message.jinja"
