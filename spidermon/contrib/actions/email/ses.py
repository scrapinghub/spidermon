from __future__ import absolute_import

import boto3

from spidermon.exceptions import NotConfigured
from spidermon.utils.settings import get_aws_credentials

from . import SendEmail


class SendSESEmail(SendEmail):
    aws_access_key = None
    aws_secret_key = None
    aws_region_name = "us-east-1"

    def __init__(
        self,
        aws_access_key=None,
        aws_secret_key=None,
        aws_region_name=None,
        *args,
        **kwargs
    ):
        super(SendSESEmail, self).__init__(*args, **kwargs)
        self.aws_access_key = aws_access_key or self.aws_access_key
        self.aws_secret_key = aws_secret_key or self.aws_secret_key
        self.aws_region_name = aws_region_name or self.aws_region_name
        if not self.fake and not self.aws_access_key:
            raise NotConfigured("You must provide the AWS Access Key.")
        if not self.fake and not self.aws_secret_key:
            raise NotConfigured("You must provide the AWS Secret Key.")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super(SendSESEmail, cls).from_crawler_kwargs(crawler)
        (aws_access_key_id, aws_secret_access_key) = get_aws_credentials(
            crawler.settings
        )
        kwargs.update(
            {
                "aws_access_key": aws_access_key_id,
                "aws_secret_key": aws_secret_access_key,
                "aws_region_name": crawler.settings.get("SPIDERMON_AWS_REGION_NAME"),
            }
        )
        return kwargs

    def _get_recipients(self):
        recipients = []
        for recipient_subset in (self.to, self.cc, self.bcc):
            if not recipient_subset:
                pass
            elif isinstance(recipient_subset, str):
                recipients.append(recipient_subset)
            else:
                recipients.extend(recipient_subset)
        return recipients

    def send_message(self, message):
        client = boto3.client(
            service_name="ses",
            region_name=self.aws_region_name,
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
        )
        client.send_raw_email(
            Source=self.sender,
            Destinations=self._get_recipients(),
            RawMessage={"Data": message.as_string()},
        )
