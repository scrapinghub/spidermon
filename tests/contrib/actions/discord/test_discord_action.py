import pytest

pytest.importorskip("jinja2")

from spidermon.contrib.actions.discord import DiscordMessageManager
from spidermon.exceptions import NotConfigured


@pytest.fixture
def logger_info(mocker):
    return mocker.patch("spidermon.contrib.actions.discord.logger.info")


@pytest.fixture
def request_post(mocker):
    return mocker.patch("spidermon.contrib.actions.discord.requests.post")


def test_log_text_when_fake_set(logger_info):
    text_to_be_logged = "text to be logged"

    manager = DiscordMessageManager("discord-webhook-url", fake=True)
    manager.send_message(text_to_be_logged)

    assert logger_info.call_count == 1
    assert text_to_be_logged in logger_info.call_args[0]


def test_do_not_log_text_when_fake_is_not_set(request_post, logger_info):
    text_not_to_be_logged = "text not to be logged"

    manager = DiscordMessageManager("discord-webhook-url", fake=False)
    manager.send_message(text_not_to_be_logged)

    assert logger_info.call_count == 0


def test_fail_if_no_webhook_url():
    with pytest.raises(NotConfigured):
        DiscordMessageManager(None, fake=False)


def test_send_message(request_post):
    manager = DiscordMessageManager("discord-webhook-url", fake=False)
    manager.send_message("message")
    assert request_post.call_count == 1


def test_log_error_when_api_return_an_error(mocker, request_post):
    request_post.return_value.ok = False
    request_post.return_value.reason = "Fail Reason"

    logger_error = mocker.patch("spidermon.contrib.actions.discord.logger.error")
    error_message = "Failed to send message. Discord API error: Fail Reason"

    manager = DiscordMessageManager("discord-webhook-url", fake=False)
    manager.send_message("Hello")

    assert logger_error.call_count == 1
    assert error_message == logger_error.call_args[0][0]
