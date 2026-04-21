from scrapy.mail import MailSender

from spidermon.exceptions import NotConfigured

from . import SendEmail

DEFAULT_SMTP_ENFORCE_TLS = False
DEFAULT_SMTP_ENFORCE_SSL = False
DEFAULT_SMTP_PORT = 25


class SendSmtpEmail(SendEmail):
    def __init__(self, smtp_settings=None, *args, **kwargs):
        smtp_host = kwargs.pop("smtp_host", None)
        smtp_port = kwargs.pop("smtp_port", None)
        smtp_user = kwargs.pop("smtp_user", None)
        smtp_password = kwargs.pop("smtp_password", None)
        smtp_enforce_tls = kwargs.pop("smtp_enforce_tls", None)
        smtp_enforce_ssl = kwargs.pop("smtp_enforce_ssl", None)
        if smtp_settings:
            if smtp_host is None:
                smtp_host = smtp_settings.get("smtp_host")
            if smtp_port is None:
                smtp_port = smtp_settings.get("smtp_port")
            if smtp_user is None:
                smtp_user = smtp_settings.get("smtp_user")
            if smtp_password is None:
                smtp_password = smtp_settings.get("smtp_password")
            if smtp_enforce_tls is None:
                smtp_enforce_tls = smtp_settings.get("smtp_enforce_tls")
            if smtp_enforce_ssl is None:
                smtp_enforce_ssl = smtp_settings.get("smtp_enforce_ssl")

        super().__init__(*args, **kwargs)

        self.smtp_host = smtp_host
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.smtp_port = smtp_port or DEFAULT_SMTP_PORT
        self.smtp_enforce_tls = (
            smtp_enforce_tls
            if smtp_enforce_tls is not None
            else DEFAULT_SMTP_ENFORCE_TLS
        )
        self.smtp_enforce_ssl = (
            smtp_enforce_ssl
            if smtp_enforce_ssl is not None
            else DEFAULT_SMTP_ENFORCE_SSL
        )

        if not self.smtp_host:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_SMTP_HOST setting.",
            )
        if not self.smtp_user:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_SMTP_USER setting.",
            )
        if not self.smtp_password:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_SMTP_PASSWORD setting.",
            )

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super().from_crawler_kwargs(crawler)
        kwargs.update(
            {
                "smtp_host": crawler.settings.get("SPIDERMON_SMTP_HOST"),
                "smtp_port": crawler.settings.getint("SPIDERMON_SMTP_PORT") or None,
                "smtp_user": crawler.settings.get("SPIDERMON_SMTP_USER"),
                "smtp_password": crawler.settings.get("SPIDERMON_SMTP_PASSWORD"),
                "smtp_enforce_tls": crawler.settings.getbool(
                    "SPIDERMON_SMTP_ENFORCE_TLS",
                )
                if "SPIDERMON_SMTP_ENFORCE_TLS" in crawler.settings
                else None,
                "smtp_enforce_ssl": crawler.settings.getbool(
                    "SPIDERMON_SMTP_ENFORCE_SSL",
                )
                if "SPIDERMON_SMTP_ENFORCE_SSL" in crawler.settings
                else None,
            },
        )
        return kwargs

    def send_message(self, message, **kwargs):
        mail_sender = MailSender(
            smtphost=self.smtp_host,
            mailfrom=self.sender,
            smtpuser=self.smtp_user,
            smtppass=self.smtp_password,
            smtpport=self.smtp_port,
            smtptls=self.smtp_enforce_tls,
            smtpssl=self.smtp_enforce_ssl,
        )

        mail_sender.send(
            to=self.to,
            subject=message["Subject"],
            body=message.as_string(),
            cc=self.cc,
            _callback=kwargs.get("_callback"),
        )
