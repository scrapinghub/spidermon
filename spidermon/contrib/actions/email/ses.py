import boto3

from spidermon.exceptions import NotConfigured
from spidermon.utils.settings import get_aws_credentials

from . import SendEmail


class SendSESEmail(SendEmail):
    aws_access_key = None
    aws_secret_key = None
    aws_region_name = "us-east-1"
    aws_return_path = None

    def __init__(
        self,
        aws_access_key=None,
        aws_secret_key=None,
        aws_region_name=None,
        aws_return_path=None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.aws_access_key = aws_access_key or self.aws_access_key
        self.aws_secret_key = aws_secret_key or self.aws_secret_key
        self.aws_region_name = aws_region_name or self.aws_region_name
        self.aws_return_path = aws_return_path or self.aws_return_path
        if not self.fake and not self.aws_access_key:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_AWS_ACCESS_KEY_ID setting."
            )
        if not self.fake and not self.aws_secret_key:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_AWS_SECRET_ACCESS_KEY setting."
            )

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        kwargs = super().from_crawler_kwargs(crawler)
        (aws_access_key_id, aws_secret_access_key) = get_aws_credentials(
            crawler.settings
        )
        kwargs.update(
            {
                "aws_access_key": aws_access_key_id,
                "aws_secret_key": aws_secret_access_key,
                "aws_region_name": crawler.settings.get("SPIDERMON_AWS_REGION_NAME"),
                "aws_return_path": crawler.settings.get("SPIDERMON_AWS_RETURN_PATH"),
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

    def send_message(self, message, **kwargs):
        client = boto3.client(
            service_name="ses",
            region_name=self.aws_region_name,
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
        )

        raw_message = {"Data": message.as_string()}
        if self.aws_return_path:
            raw_message["X-SES-RETURN-PATH-ARN"] = self.aws_return_path

        client.send_raw_email(
            Source=self.sender,
            Destinations=self._get_recipients(),
            RawMessage=raw_message,
        )
