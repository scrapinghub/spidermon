import pytest

pytest.importorskip("jinja2")

from unittest.mock import MagicMock, patch

from spidermon.contrib.actions.slack import SendSlackMessage, SlackMessageManager


@pytest.fixture
def logger_info(mocker):
    return mocker.patch("spidermon.contrib.actions.slack.logger.info")


def test_log_text_when_fake_set(logger_info):
    text_to_be_logged = "text to be logged"

    manager = SlackMessageManager(
        sender_token="anything",
        sender_name="someone",
        fake=True,
    )
    manager.send_message(to=["someone"], text=text_to_be_logged)

    assert logger_info.call_count == 1
    assert text_to_be_logged in logger_info.call_args[0]


def test_log_text_and_attachment_when_fake_set(logger_info):
    text_to_be_logged = "text to be logged"
    attach_to_be_logged = "attachment content"

    manager = SlackMessageManager(
        sender_token="anything",
        sender_name="@someone",
        fake=True,
    )
    manager.send_message(to=[], text=text_to_be_logged, attachments=attach_to_be_logged)

    assert logger_info.call_count == 2
    assert text_to_be_logged in logger_info.call_args_list[0][0]
    assert attach_to_be_logged in logger_info.call_args_list[1][0]


def test_do_not_log_text_when_fake_is_not_set(logger_info):
    text_not_to_be_logged = "text not to be logged"

    manager = SlackMessageManager(
        sender_token="anything",
        sender_name="@someone",
        fake=False,
    )
    manager.send_message(to=[], text=text_not_to_be_logged)

    assert logger_info.call_count == 0


def test_do_not_log_text_and_attach_when_fake_is_not_set(logger_info):
    text_not_to_be_logged = "text not to be logged"
    attach_not_to_be_logged = "attachment content"

    manager = SlackMessageManager(
        sender_token="anything",
        sender_name="@someone",
        fake=False,
    )
    manager.send_message(
        to=[],
        text=text_not_to_be_logged,
        attachments=attach_not_to_be_logged,
    )

    assert logger_info.call_count == 0


@patch("spidermon.contrib.actions.slack.WebClient")
def test_pass_arbitrary_args_to_manager_send_message_channel(slack_mock):
    manager = SlackMessageManager(
        sender_token="anything",
        sender_name="@someone",
    )

    manager.send_message(
        to=["channel"],
        text="a message",
        use_mention=True,
        arbitrary_arg=True,
    )

    _, kwargs = manager._client.chat_postMessage.call_args_list[0]
    assert "arbitrary_arg" in kwargs


@patch("spidermon.contrib.actions.slack.WebClient")
def test_pass_arbitrary_args_to_manager_send_message_user(slack_mock):
    manager = SlackMessageManager(
        sender_token="anything",
        sender_name="@someone",
    )

    manager._users = {"user": {"id": 10}}

    manager.send_message(
        to=["@user"],
        text="a message",
        use_mention=True,
        arbitrary_arg=True,
    )

    _, kwargs = manager._client.chat_postMessage.call_args_list[0]
    assert "arbitrary_arg" in kwargs


def test_message_sender_pass_kwargs():
    sender = SendSlackMessage(
        sender_token="anything",
        sender_name="@someone",
        recipients=["user"],
        a_new_arg="hello",
    )

    sender.manager._client = MagicMock()
    sender.get_message = MagicMock()
    sender.get_attachments = MagicMock()

    sender.get_message.return_value = "a message"
    sender.get_attachments.return_value = None

    sender.run_action()

    _, kwargs = sender.manager._client.chat_postMessage.call_args_list[0]
    assert "a_new_arg" in kwargs
