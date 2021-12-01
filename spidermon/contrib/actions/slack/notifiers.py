from . import SendSlackMessage


class SendSlackMessageSpiderStarted(SendSlackMessage):
    message_template = "slack/spider/notifier/start/message.jinja"
    include_attachments = False


class SendSlackMessageSpiderFinished(SendSlackMessage):
    message_template = "slack/spider/notifier/finish/message.jinja"
    attachments_template = "slack/spider/notifier/finish/attachments.jinja"
    include_ok_attachments = False
    include_error_attachments = True
    include_report_link = True
    report_index = 0

    def __init__(
        self,
        include_ok_attachments=None,
        include_error_attachments=None,
        include_report_link=None,
        report_index=None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.include_ok_attachments = (
            include_ok_attachments or self.include_ok_attachments
        )
        if include_error_attachments is not None:
            self.include_error_attachments = include_error_attachments

        if include_report_link is not None:
            self.include_report_link = include_report_link

        self.report_index = report_index or self.report_index

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super().from_crawler_kwargs(crawler)
        kwargs.update(
            {
                "include_ok_attachments": crawler.settings.get(
                    "SPIDERMON_SLACK_NOTIFIER_INCLUDE_OK_ATTACHMENTS"
                ),
                "include_error_attachments": crawler.settings.get(
                    "SPIDERMON_SLACK_NOTIFIER_INCLUDE_ERROR_ATTACHMENTS"
                ),
                "include_report_link": crawler.settings.get(
                    "SPIDERMON_SLACK_NOTIFIER_INCLUDE_REPORT_LINK"
                ),
                "report_index": crawler.settings.get(
                    "SPIDERMON_SLACK_NOTIFIER_REPORT_INDEX"
                ),
            }
        )
        return kwargs

    def get_attachments(self):
        if (self.monitors_failed and self.include_error_attachments) or (
            self.monitors_passed and self.include_ok_attachments
        ):
            return super().get_attachments()
        else:
            return None

    def get_template_context(self):
        context = super().get_template_context()
        context.update(
            {
                "include_ok_attachments": self.include_ok_attachments,
                "include_error_attachments": self.include_error_attachments,
                "include_report_link": self.include_report_link,
                "report_index": self.report_index,
            }
        )
        return context


class SendSlackMessageSpiderRunning(SendSlackMessageSpiderFinished):
    message_template = "slack/spider/notifier/periodic/message.jinja"
    attachments_template = "slack/spider/notifier/periodic/attachments.jinja"
