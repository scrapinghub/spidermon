import pytest

from spidermon.exceptions import NotConfigured
from spidermon.contrib.actions.telegram import (
    TelegramMessageManager,
    SimplyTelegramClient,
)


@pytest.fixture
def logger_info(mocker):
    return mocker.patch("spidermon.contrib.actions.telegram.logger.info")


@pytest.fixture
def client_send_message(mocker):
    return mocker.patch(
        "spidermon.contrib.actions.telegram.SimplyTelegramClient.send_message"
    )


@pytest.fixture
def request_get(mocker):
    return mocker.patch("spidermon.contrib.actions.telegram.requests.get")


def test_log_text_when_fake_set(logger_info):
    text_to_be_logged = "text to be logged"

    manager = TelegramMessageManager(sender_token="anything", fake=True)
    manager.send_message(to=["someone"], text=text_to_be_logged)

    assert logger_info.call_count == 1
    assert text_to_be_logged in logger_info.call_args[0]


def test_do_not_log_text_when_fake_is_not_set(logger_info):
    text_not_to_be_logged = "text not to be logged"

    manager = TelegramMessageManager(sender_token="anything", fake=False)
    manager.send_message(to=[], text=text_not_to_be_logged)

    assert logger_info.call_count == 0


def test_fail_if_no_token():
    with pytest.raises(NotConfigured):
        TelegramMessageManager(sender_token=None, fake=False)


@pytest.mark.parametrize("recipients,call_count", [("1234", 1), (["1234", "4321"], 2)])
def test_send_message(client_send_message, recipients, call_count):
    manager = TelegramMessageManager(sender_token="anything", fake=False)
    manager.send_message(to=recipients, text="message")
    assert client_send_message.call_count == call_count


def test_simply_telegram_client(request_get):
    client = SimplyTelegramClient(token="token")
    client.send_message("message", "1234")
    assert request_get.call_count == 1
