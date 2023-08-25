import boto3
import logging

from spidermon.exceptions import NotConfigured
from spidermon.contrib.actions.templates import ActionWithTemplates

logger = logging.getLogger(__name__)


class BaseSNSNotification(ActionWithTemplates):
    aws_access_key = None
    aws_secret_key = None
    aws_region_name = "us-east-1"
    topic_arn = None

    def __init__(
        self,
        topic_arn=None,
        aws_access_key=None,
        aws_secret_key=None,
        aws_region_name=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.topic_arn = topic_arn or self.topic_arn
        self.aws_access_key = aws_access_key or self.aws_access_key
        self.aws_secret_key = aws_secret_key or self.aws_secret_key
        self.aws_region_name = aws_region_name or self.aws_region_name

        if not self.topic_arn:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_SNS_TOPIC_ARN setting."
            )
        if not self.aws_access_key:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_AWS_ACCESS_KEY_ID setting."
            )
        if not self.aws_secret_key:
            raise NotConfigured(
                "You must provide a value for SPIDERMON_AWS_SECRET_ACCESS_KEY setting."
            )

    def run_action(self):
        self.send_message()

    def send_message(self, subject, attributes):
        client = boto3.client(
            service_name="sns",
            region_name=self.aws_region_name,
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
        )
        logger.info(
            f"Sending SNS message with subject: {subject} and attributes: {attributes}"
        )
        try:
            client.publish(
                TopicArn=self.topic_arn, Message=subject, MessageAttributes=attributes
            )
        except Exception as e:
            logger.error(f"Failed to send SNS message: {e}")
            raise
        logger.info(f"SNS message sent successfully!")

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        return {
            "topic_arn": crawler.settings.get("SPIDERMON_SNS_TOPIC_ARN"),
            "aws_access_key": crawler.settings.get("SPIDERMON_AWS_ACCESS_KEY_ID"),
            "aws_secret_key": crawler.settings.get("SPIDERMON_AWS_SECRET_ACCESS_KEY"),
        }


class SendSNSNotification(BaseSNSNotification):
    def send_message(self, subject, body):
        client = boto3.client(
            service_name="sns",
            region_name=self.aws_region_name,
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
        )
        client.publish(TopicArn=self.topic_arn, Message=body, Subject=subject)
