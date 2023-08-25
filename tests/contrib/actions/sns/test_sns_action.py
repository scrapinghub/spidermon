import pytest

from scrapy.utils.test import get_crawler
from spidermon.exceptions import NotConfigured
from spidermon.contrib.actions.sns import BaseSNSNotification
from spidermon.contrib.actions.sns.notifiers import (
    SendSNSNotificationSpiderFinished,
    SendSNSNotificationSpiderStarted,
)


@pytest.fixture
def boto3_client(mocker):
    return mocker.patch("spidermon.contrib.actions.sns.boto3.client")


@pytest.fixture
def logger_info(mocker):
    return mocker.patch("spidermon.contrib.actions.sns.logger.info")


@pytest.fixture
def logger_error(mocker):
    return mocker.patch("spidermon.contrib.actions.sns.logger.error")


@pytest.fixture
def mock_notifier_data(mocker):
    data = mocker.MagicMock()
    data.spider.name = "TestSpider"
    data.stats.start_time = "2023-08-25 10:00:00"
    data.stats.finish_time = "2023-08-25 11:00:00"
    data.stats.item_scraped_count = 100
    return data


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


def test_send_sns_notification_spider_started(mocker, mock_notifier_data):
    notifier = SendSNSNotificationSpiderStarted(
        topic_arn="arn:aws:sns:us-east-1:123456789012:MyTopic",
        aws_access_key="ACCESS_KEY",
        aws_secret_key="SECRET_KEY",
    )
    notifier.data = mock_notifier_data

    expected_subject = "Spider Started"
    expected_attributes = {
        "EventType": {"DataType": "String", "StringValue": "SpiderStarted"},
        "SpiderName": {"DataType": "String", "StringValue": "TestSpider"},
        "StartTime": {"DataType": "String", "StringValue": "2023-08-25 10:00:00"},
    }

    mock_send_message = mocker.patch.object(notifier, "send_message")
    notifier.run_action()
    mock_send_message.assert_called_once_with(expected_subject, expected_attributes)


def test_send_sns_notification_spider_finished(mocker, mock_notifier_data):
    notifier = SendSNSNotificationSpiderFinished(
        topic_arn="arn:aws:sns:us-east-1:123456789012:MyTopic",
        aws_access_key="ACCESS_KEY",
        aws_secret_key="SECRET_KEY",
    )
    notifier.data = mock_notifier_data

    expected_subject = "Spider Finished"
    expected_attributes = {
        "EventType": {"DataType": "String", "StringValue": "SpiderFinished"},
        "SpiderName": {"DataType": "String", "StringValue": "TestSpider"},
        "ItemsScraped": {"DataType": "Number", "StringValue": "100"},
        "FinishTime": {"DataType": "String", "StringValue": "2023-08-25 11:00:00"},
    }

    mock_send_message = mocker.patch.object(notifier, "send_message")
    notifier.run_action()
    mock_send_message.assert_called_once_with(expected_subject, expected_attributes)
