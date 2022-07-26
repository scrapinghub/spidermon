import sys
import pytest
from unittest.mock import MagicMock

from spidermon.contrib.actions.slack import SlackMessageManager


@pytest.fixture
def logger_info(mocker):
    return mocker.patch("spidermon.contrib.actions.slack.logger.info")


def test_log_text_when_fake_set(logger_info):
    text_to_be_logged = "text to be logged"

    manager = SlackMessageManager(
        sender_token="anything", sender_name="someone", fake=True
    )
    manager.send_message(to=["someone"], text=text_to_be_logged)

    assert logger_info.call_count == 1
    assert text_to_be_logged in logger_info.call_args[0]


def test_log_text_and_attachment_when_fake_set(logger_info):
    text_to_be_logged = "text to be logged"
    attach_to_be_logged = "attachment content"

    manager = SlackMessageManager(
        sender_token="anything", sender_name="@someone", fake=True
    )
    manager.send_message(to=[], text=text_to_be_logged, attachments=attach_to_be_logged)

    assert logger_info.call_count == 2
    assert text_to_be_logged in logger_info.call_args_list[0][0]
    assert attach_to_be_logged in logger_info.call_args_list[1][0]


def test_do_not_log_text_when_fake_is_not_set(logger_info):
    text_not_to_be_logged = "text not to be logged"

    manager = SlackMessageManager(
        sender_token="anything", sender_name="@someone", fake=False
    )
    manager.send_message(to=[], text=text_not_to_be_logged)

    assert logger_info.call_count == 0


def test_do_not_log_text_and_attach_when_fake_is_not_set(logger_info):
    text_not_to_be_logged = "text not to be logged"
    attach_not_to_be_logged = "attachment content"

    manager = SlackMessageManager(
        sender_token="anything", sender_name="@someone", fake=False
    )
    manager.send_message(
        to=[], text=text_not_to_be_logged, attachments=attach_not_to_be_logged
    )

    assert logger_info.call_count == 0

def test_pass_arbitrary_kwargs_to_send_message():
    manager = SlackMessageManager(
        sender_token="anything", sender_name="@someone", 
    )
    manager.send_message = MagicMock()
    manager.send_message(
        to=[], text='some_text', reply_broadcast=True,
        thread_ts='some_thread_ts_value',
        unfurl_links=False,
    )
    manager.send_message.assert_called_once_with(
        to=[], text='some_text', reply_broadcast=True,
        thread_ts='some_thread_ts_value',
        unfurl_links=False,
    )

def test_pass_arbitrary_kwargs_to_chat_postMessage():
    manager = SlackMessageManager(
        sender_token="anything", sender_name="@someone", 
    )
    manager._client.chat_postMessage = MagicMock()
    manager._client.chat_postMessage(
        to=[], text='some_text', reply_broadcast=True,
        thread_ts='some_thread_ts_value',
        unfurl_links=False,
    )
    manager._client.chat_postMessage.assert_called_once_with(
        to=[], text='some_text', reply_broadcast=True,
        thread_ts='some_thread_ts_value',
        unfurl_links=False,
    )
