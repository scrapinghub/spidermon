from . import SlackMessageAction


class SlackSpiderNotifierStart(SlackMessageAction):
    message_template = 'slack/spider/notifier/start/message.jinja'
    include_attachments = False


class SlackSpiderNotifierFinish(SlackMessageAction):
    message_template = 'slack/spider/notifier/finish/message.jinja'
    attachments_template = 'slack/spider/notifier/finish/attachments.jinja'
    include_ok_attachments = False
    include_error_attachments = True

    def __init__(self,
                 include_ok_attachments=None,
                 include_error_attachments=None,
                 **kwargs):
        super(SlackSpiderNotifierFinish, self).__init__(**kwargs)
        self.include_ok_attachments = include_ok_attachments or self.include_ok_attachments
        self.include_error_attachments = include_error_attachments or self.include_error_attachments

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(SlackSpiderNotifierFinish, cls).from_crawler_kwargs(crawler)
        kwargs.update({
            'include_ok_attachments': crawler.settings.get('SPIDERMON_SLACK_NOTIFIER_INCLUDE_OK_ATTACHMENTS'),
            'include_error_attachments': crawler.settings.get('SPIDERMON_SLACK_NOTIFIER_INCLUDE_ERROR_ATTACHMENTS'),
        })
        return kwargs

    def get_attachments(self):
        if (self.monitors_failed and self.include_error_attachments) or\
           (self.monitors_passed and self.include_ok_attachments):
            return super(SlackSpiderNotifierFinish, self).get_attachments()
        else:
            return None

    def _get_template_context(self):
        context = super(SlackSpiderNotifierFinish, self)._get_template_context()
        context.update({
            'include_ok_attachments': self.include_ok_attachments,
            'include_error_attachments': self.include_error_attachments,
        })
        return context
