import pytest

from scrapy import Spider
from scrapy.utils.test import get_crawler
from spidermon.exceptions import NotConfigured
from spidermon.contrib.actions.sns import BaseSNSNotification


# Mocking boto3 client
@pytest.fixture
def boto3_client(mocker):
    return mocker.patch("spidermon.contrib.actions.sns.boto3.client")


# Mocking logger.info
@pytest.fixture
def logger_info(mocker):
    return mocker.patch("spidermon.contrib.actions.sns.logger.info")


# Mocking logger.error
@pytest.fixture
def logger_error(mocker):
    return mocker.patch("spidermon.contrib.actions.sns.logger.error")


def test_fail_if_no_topic_arn():
    with pytest.raises(NotConfigured):
        BaseSNSNotification(topic_arn=None)


def test_fail_if_no_aws_access_key():
    with pytest.raises(NotConfigured):
        BaseSNSNotification(topic_arn="arn:aws:sns:us-east-1:123456789012:MyTopic")


def test_fail_if_no_aws_secret_key():
    with pytest.raises(NotConfigured):
        BaseSNSNotification(
            topic_arn="arn:aws:sns:us-east-1:123456789012:MyTopic",
            aws_access_key="ACCESS_KEY",
        )


def test_send_message(boto3_client, logger_info):
    notifier = BaseSNSNotification(
        topic_arn="arn:aws:sns:us-east-1:123456789012:MyTopic",
        aws_access_key="ACCESS_KEY",
        aws_secret_key="SECRET_KEY",
    )
    subject = "Test Notification"
    attributes = {"EventType": {"DataType": "String", "StringValue": "TestEvent"}}
    notifier.send_message(subject, attributes)
    assert boto3_client.call_count == 1
    assert logger_info.call_count == 2


def test_log_error_when_sns_returns_error(boto3_client, logger_error):
    boto3_client.return_value.publish.side_effect = Exception("SNS Error")
    notifier = BaseSNSNotification(
        topic_arn="arn:aws:sns:us-east-1:123456789012:MyTopic",
        aws_access_key="ACCESS_KEY",
        aws_secret_key="SECRET_KEY",
    )
    subject = "Test Notification"
    attributes = {"EventType": {"DataType": "String", "StringValue": "TestEvent"}}
    with pytest.raises(Exception, match="SNS Error"):
        notifier.send_message(subject, attributes)
    assert logger_error.call_count == 1
