import smtplib

from spidermon.exceptions import NotConfigured

from . import SendEmail

DEFAULT_SMTP_ENFORCE_TLS = False
DEFAULT_SMTP_ENFORCE_SSL = False
DEFAULT_SMTP_PORT = 25


class SendSmtpEmail(SendEmail):
    def __init__(  # noqa: PLR0913, PLR0917
        self,
        smtp_host=None,
        smtp_port=None,
        smtp_user=None,
        smtp_password=None,
        smtp_enforce_tls=None,
        smtp_enforce_ssl=None,
        *args,
        **kwargs,
    ):
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
        recipients = [*self.to, *(self.cc or []), *(self.bcc or [])]
        del message["Bcc"]

        smtp_cls = smtplib.SMTP_SSL if self.smtp_enforce_ssl else smtplib.SMTP
        with smtp_cls(self.smtp_host, self.smtp_port) as smtp:
            if self.smtp_enforce_tls:
                smtp.starttls()
            smtp.login(self.smtp_user, self.smtp_password)
            smtp.sendmail(self.sender, recipients, message.as_string())
