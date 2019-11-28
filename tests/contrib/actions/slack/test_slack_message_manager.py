import pytest

from scrapy.crawler import CrawlerRunner
from scrapy.spiders import Spider

from spidermon.contrib.actions.slack import (
    SlackMessageManager,
    SendSlackMessage,
)


def get_crawler(settings: dict = None):
    runner = CrawlerRunner(settings)
    return runner.create_crawler(Spider)


@pytest.fixture
def logger_error(mocker):
    return mocker.patch("spidermon.contrib.actions.slack.logger.error")


def test_api_call_with_no_error_should_not_log_messages(mocker, logger_error):
    api_valid_message = {"ok": True, "text": "valid response"}
    mocker.patch(
        "spidermon.contrib.actions.slack.SlackClient.api_call",
        return_value=api_valid_message,
    )
    manager = SlackMessageManager("SENDER_TOKEN", "SENDER_NAME")

    manager._api_call("some_method")

    assert logger_error.call_count == 0


def test_api_call_with_error_should_log_error_msg(mocker, logger_error):
    error_msg = "API call failure"
    # API call response with error (see https://api.slack.com/rtm#errors)
    api_error_message = {
        "ok": False,
        "reply_to": 1,
        "error": {"code": 2, "msg": error_msg},
    }
    mocker.patch(
        "spidermon.contrib.actions.slack.SlackClient.api_call",
        return_value=api_error_message,
    )

    manager = SlackMessageManager("SENDER_TOKEN", "SENDER_NAME")

    manager._api_call("some_method")

    assert logger_error.call_count == 1
    assert error_msg in logger_error.call_args_list[0][0]


def test_load_recipients_list_from_crawler_settings():
    settings = {
        'SPIDERMON_SLACK_RECIPIENTS': 'foo,bar',
    }
    crawler = get_crawler(settings)
    sender = SendSlackMessage.from_crawler_kwargs(crawler)
    assert sender['recipients'] == ['foo', 'bar']
