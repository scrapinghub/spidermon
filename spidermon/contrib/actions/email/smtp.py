from __future__ import absolute_import
import smtplib

from spidermon.exceptions import NotConfigured

from . import SendEmail


class SendSmtpEmail(SendEmail):
    smtp_host = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = None
    smtp_password = None
    
    def __init__(
        self,
        smtp_host=None,
        smtp_port=None,
        smtp_user=None,
        smtp_password=None,        
        *args,
        **kwargs
    ):
        super(SendSmtpEmail, self).__init__(*args, **kwargs)
        self.smtp_host = smtp_host or self.smtp_host
        self.smtp_port = smtp_port or self.smtp_port
        self.smtp_user = smtp_user or self.smtp_user
        self.smtp_password = smtp_password or self.smtp_password

        if not self.fake and not self.smtp_user:
            raise NotConfigured("You must provide the smtp user.")
        if not self.fake and not self.smtp_password:
            raise NotConfigured("You must provide the smtp password.")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(SendSmtpEmail, cls).from_crawler_kwargs(crawler)
        kwargs.update(
            {
                "smtp_host": crawler.settings.get("SPIDERMON_SMTP_HOST"),
                "smtp_port": crawler.settings.get("SPIDERMON_SMTP_PORT"),
                "smtp_user": crawler.settings.get("SPIDERMON_SMTP_USER"),
                "smtp_password": crawler.settings.get("SPIDERMON_SMTP_PASSWORD"),
            }
        )
        return kwargs

    def send_message(self, message):       
        if not self.sender:
            raise NotConfigured("You must provide the sender.")
        if not self.to:
            raise NotConfigured("You must provide the receiver.")

        if not self.sender or not self.to:
            return

        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        server.starttls()
        server.login(self.smtp_user, self.smtp_password)
        text = message.as_string()
        server.sendmail(self.sender, self.to, text)
        server.quit()
