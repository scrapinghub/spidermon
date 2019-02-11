from __future__ import absolute_import
import boto

from spidermon.exceptions import NotConfigured

from . import SendEmail


class SendSESEmail(SendEmail):
    aws_access_key = None
    aws_secret_key = None

    def __init__(self, aws_access_key=None, aws_secret_key=None, *args, **kwargs):
        super(SendSESEmail, self).__init__(*args, **kwargs)
        self.aws_access_key = aws_access_key or self.aws_access_key
        self.aws_secret_key = aws_secret_key or self.aws_secret_key
        if not self.fake and not self.aws_access_key:
            raise NotConfigured("You must provide the AWS Access Key.")
        if not self.fake and not self.aws_secret_key:
            raise NotConfigured("You must provide the AWS Secret Key.")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(SendSESEmail, cls).from_crawler_kwargs(crawler)
        kwargs.update(
            {
                "aws_access_key": crawler.settings.get("SPIDERMON_AWS_ACCESS_KEY"),
                "aws_secret_key": crawler.settings.get("SPIDERMON_AWS_SECRET_KEY"),
            }
        )
        return kwargs

    def send_message(self, message):
        session = boto.connect_ses(self.aws_access_key, self.aws_secret_key)
        session.send_raw_email(raw_message=message.as_string())
