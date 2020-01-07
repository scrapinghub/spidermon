from __future__ import absolute_import
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)

from spidermon.contrib.actions.templates import ActionWithTemplates
from spidermon.exceptions import NotConfigured

from premailer import transform


class SendEmail(ActionWithTemplates):
    sender = None
    subject = None
    subject_template = None
    to = None
    cc = None
    bcc = None
    reply_to = None
    body_text = None
    body_text_template = None
    body_html = None
    body_html_template = "reports/email/monitors/result.jinja"
    fake = False

    def __init__(
        self,
        sender,
        to,
        cc=None,
        bcc=None,
        reply_to=None,
        subject=None,
        subject_template=None,
        body_text=None,
        body_text_template=None,
        body_html=None,
        body_html_template=None,
        fake=None,
        *args,
        **kwargs
    ):
        super(SendEmail, self).__init__(*args, **kwargs)
        self.sender = sender or self.sender
        self.subject = subject or self.subject
        self.subject_template = subject_template or self.subject_template
        self.to = to or self.to
        self.cc = cc or self.cc
        self.bcc = bcc or self.bcc
        self.reply_to = reply_to or self.reply_to
        self.body_text = body_text or self.body_text
        self.body_text_template = body_text_template or self.body_text_template
        self.body_html = body_html or self.body_html
        self.body_html_template = body_html_template or self.body_html_template
        self.fake = fake or self.fake
        if not self.fake and not self.to:
            raise NotConfigured(
                "You must provide at least one recipient for the message."
            )
        if not self.subject:
            raise NotConfigured("You must provide a subject for the message.")
        if not (
            self.body_text or body_text_template or body_html or self.body_html_template
        ):
            raise NotConfigured("You must provide a body for the message.")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        return {
            "sender": crawler.settings.get("SPIDERMON_EMAIL_SENDER"),
            "subject": crawler.settings.get("SPIDERMON_EMAIL_SUBJECT"),
            "subject_template": crawler.settings.get(
                "SPIDERMON_EMAIL_SUBJECT_TEMPLATE"
            ),
            "to": cls.getlist(crawler.settings, "SPIDERMON_EMAIL_TO"),
            "cc": cls.getlist(crawler.settings, "SPIDERMON_EMAIL_CC"),
            "bcc": cls.getlist(crawler.settings, "SPIDERMON_EMAIL_BCC"),
            "reply_to": crawler.settings.get("SPIDERMON_EMAIL_REPLY_TO"),
            "body_text": crawler.settings.get("SPIDERMON_BODY_TEXT"),
            "body_text_template": crawler.settings.get("SPIDERMON_BODY_TEXT_TEMPLATE"),
            "body_html": crawler.settings.get("SPIDERMON_BODY_HTML"),
            "body_html_template": crawler.settings.get("SPIDERMON_BODY_HTML_TEMPLATE"),
            "fake": crawler.settings.getbool("SPIDERMON_EMAIL_FAKE"),
            "context": crawler.settings.getdict("SPIDERMON_EMAIL_CONTEXT"),
        }

    @staticmethod
    def getlist(settings, entry):
        return [v.strip() for v in settings.getlist(entry)]

    def run_action(self):
        message = self.get_message()
        if self.fake:
            logger.info(message.as_string())
        else:
            self.send_message(message)

    def get_subject(self):
        if self.subject:
            return self.render_text_template(self.subject)
        elif self.subject_template:
            return self.render_template(self.subject_template)
        else:
            return ""

    def get_body_text(self):
        if self.body_text:
            return self.render_text_template(self.body_text)
        elif self.body_text_template:
            return self.render_template(self.body_text_template)
        else:
            return ""

    def get_body_html(self):
        html = ""
        if self.body_html:
            html = transform(self.render_text_template(self.body_html))
        elif self.body_html_template:
            html = transform(self.render_template(self.body_html_template))
        return html

    def get_message(self):
        subject = self.get_subject()
        body_text = self.get_body_text()
        body_html = self.get_body_html()

        message = MIMEMultipart("alternative")
        message.set_charset("UTF-8")

        message["Subject"] = subject
        message["From"] = self.sender
        message["To"] = ", ".join(self.to)
        if self.cc:
            message["Cc"] = ", ".join(self.cc)
        if self.bcc:
            message["Bcc"] = ", ".join(self.bcc)
        if self.reply_to:
            message["reply-to"] = self.reply_to

        message.attach(MIMEText(body_text, "plain"))
        if body_html:
            message.attach(MIMEText(body_html, "html"))

        return message

    def send_message(self, message):
        raise NotImplementedError
