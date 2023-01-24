from unittest.mock import patch, MagicMock
from spidermon.contrib.actions.email.ses import SendSESEmail

import pytest
from scrapy.utils.test import get_crawler
from scrapy import Spider


@pytest.fixture
def test_settings():
    return {
        "SPIDERMON_AWS_REGION_NAME": "fake",
        "SPIDERMON_AWS_ACCESS_KEY": "fake",
        "SPIDERMON_AWS_SECRET_KEY": "fake",
        "SPIDERMON_EMAIL_TO": "fake@test.com",
        "SPIDERMON_EMAIL_SUBJECT": "fake",
        "SPIDERMON_BODY_TEXT_TEMPLATE": "fake"
    }


def run_mailer(test_settings):
    mock_spider = MagicMock()
    mock_spider.name = "test"

    crawler = get_crawler(Spider, test_settings)
    mailer = SendSESEmail.from_crawler(crawler)
    mailer.send_message(MagicMock())


@patch("spidermon.contrib.actions.email.ses.boto")
def test_ses_no_return_path(mock_boto3, test_settings):
    run_mailer(test_settings)

    mock_boto3.client().send_raw_email.assert_called()

    message = mock_boto3.client().send_raw_email.call_args.kwargs['RawMessage']
    assert message.get("X-SES-RETURN-PATH-ARN") is None


@patch("spidermon.contrib.actions.email.ses.boto")
def test_ses_return_path(mock_boto3, test_settings):
    test_settings["SPIDERMON_AWS_RETURN_PATH"] = "return@path.com"
    run_mailer(test_settings)

    mock_boto3.client().send_raw_email.assert_called()

    message = mock_boto3.client().send_raw_email.call_args.kwargs['RawMessage']
    assert message.get("X-SES-RETURN-PATH-ARN") == "return@path.com"

