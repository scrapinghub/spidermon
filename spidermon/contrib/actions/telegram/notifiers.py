from __future__ import absolute_import
from . import SendTelegramMessage


class SendTelegramMessageSpiderStarted(SendTelegramMessage):
    message_template = "telegram/spider/notifier/start/message.jinja"


class SendTelegramMessageSpiderFinished(SendTelegramMessage):
    message_template = "telegram/spider/notifier/finish/message.jinja"
    include_ok_messages = False
    include_error_messages = True

    def __init__(
        self, include_ok_messages=None, include_error_messages=None, *args, **kwargs
    ):
        super(SendTelegramMessageSpiderFinished, self).__init__(*args, **kwargs)
        self.include_ok_messages = include_ok_messages or self.include_ok_messages
        self.include_error_messages = (
            include_error_messages or self.include_error_messages
        )

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(SendTelegramMessageSpiderFinished, cls).from_crawler_kwargs(
            crawler
        )
        kwargs.update(
            {
                "include_ok_messages": crawler.settings.get(
                    "SPIDERMON_TELEGRAM_NOTIFIER_INCLUDE_OK_MESSAGES"
                ),
                "include_error_messages": crawler.settings.get(
                    "SPIDERMON_TELEGRAM_NOTIFIER_INCLUDE_ERROR_MESSAGES"
                ),
            }
        )
        return kwargs

    def get_template_context(self):
        context = super(SendTelegramMessageSpiderFinished, self).get_template_context()
        context.update(
            {
                "include_ok_messages": self.include_ok_messages,
                "include_error_messages": self.include_error_messages,
            }
        )
        return context


class SendTelegramMessageSpiderRunning(SendTelegramMessageSpiderFinished):
    message_template = "telegram/spider/notifier/periodic/message.jinja"
