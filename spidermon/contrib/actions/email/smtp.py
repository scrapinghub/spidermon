from __future__ import absolute_import

from spidermon.exceptions import NotConfigured
from scrapy.mail import MailSender

from . import SendEmail


class SendSmtpEmail(SendEmail):
    def __init__(
        self,
        smtp_host=None,
        smtp_port=25,
        smtp_user=None,
        smtp_password=None,
        smtp_ssl=False,
        *args,
        **kwargs
    ):
        super(SendSmtpEmail, self).__init__(*args, **kwargs)
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.smtp_ssl = smtp_ssl

        if not self.fake and not self.smtp_host:
            raise NotConfigured("YOU MUST PROVIDE THE SMTP HOST.")
        if not self.fake and not self.smtp_user:
            raise NotConfigured("YOU MUST PROVIDE THE SMTP USER.")
        if not self.fake and not self.smtp_password:
            raise NotConfigured("YOU MUST PROVIDE THE SMTP PASSWORD.")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(SendSmtpEmail, cls).from_crawler_kwargs(crawler)
        kwargs.update(
            {
                "smtp_host": crawler.settings.get("SPIDERMON_SMTP_HOST"),
                "smtp_port": crawler.settings.getint("SPIDERMON_SMTP_PORT"),
                "smtp_user": crawler.settings.get("SPIDERMON_SMTP_USER"),
                "smtp_password": crawler.settings.get("SPIDERMON_SMTP_PASSWORD"),
                "smtp_ssl": crawler.settings.getbool("SPIDERMON_SMTP_SSL"),
            }
        )
        return kwargs

    def send_message(self, message, **kwargs):
        if not self.sender:
            raise NotConfigured("You must provide the sender.")

        if not self.sender or not self.to:
            return

        server = MailSender(
            self.smtp_host,
            self.sender,
            self.smtp_user,
            self.smtp_password,
            self.smtp_port,
            smtpssl=self.smtp_ssl,
            debug=bool(kwargs.get("debug")),
        )

        server.send(
            to=self.to,
            subject=message["Subject"],
            body=message.as_string(),
            cc=self.cc,
            _callback=kwargs.get("_callback"),
        )
