import json
from typing import TYPE_CHECKING, Any

import pytest
from pytest_mock import MockerFixture, MockType

if TYPE_CHECKING:
    from collections.abc import Callable

    from scrapy.crawler import Crawler

pytest.importorskip("scrapy")

from spidermon.contrib.actions.telegram import (
    SendTelegramMessage,
    SimplyTelegramClient,
    TelegramMessageManager,
)
from spidermon.contrib.actions.telegram.notifiers import (
    SendTelegramMessageSpiderFinished,
)
from spidermon.exceptions import NotConfigured


@pytest.fixture
def logger_info(mocker: MockerFixture) -> MockType:
    return mocker.patch("spidermon.contrib.actions.telegram.logger.info")


@pytest.fixture
def client_send_message(mocker: MockerFixture) -> MockType:
    return mocker.patch(
        "spidermon.contrib.actions.telegram.SimplyTelegramClient.send_message",
    )


@pytest.fixture
def request_get(mocker: MockerFixture) -> MockType:
    return mocker.patch("spidermon.contrib.actions.telegram.requests.get")


def test_log_text_when_fake_set(logger_info: MockType) -> None:
    text_to_be_logged = "text to be logged"

    manager = TelegramMessageManager(sender_token="anything", fake=True)
    manager.send_message(to=["someone"], text=text_to_be_logged)

    assert logger_info.call_count == 1
    assert text_to_be_logged in logger_info.call_args[0]


def test_do_not_log_text_when_fake_is_not_set(logger_info: MockType) -> None:
    text_not_to_be_logged = "text not to be logged"

    manager = TelegramMessageManager(sender_token="anything", fake=False)
    manager.send_message(to=[], text=text_not_to_be_logged)

    assert logger_info.call_count == 0


def test_fail_if_no_token() -> None:
    with pytest.raises(NotConfigured):
        TelegramMessageManager(sender_token=None, fake=False)


def test_fail_if_no_recipients() -> None:
    with pytest.raises(NotConfigured):
        SendTelegramMessage(sender_token="token")

    with pytest.raises(NotConfigured):
        SendTelegramMessage(sender_token="token", fake=True)


@pytest.mark.parametrize(
    ("recipients", "call_count"),
    [(["1234"], 1), (["1234", "4321"], 2)],
)
def test_send_message(
    client_send_message: MockType, recipients: Any, call_count: int
) -> None:
    manager = TelegramMessageManager(sender_token="anything", fake=False)
    manager.send_message(to=recipients, text="message")
    assert client_send_message.call_count == call_count


def test_simply_telegram_client(request_get: MockType) -> None:
    client = SimplyTelegramClient(token="token")
    client.send_message("message", "1234")
    assert request_get.call_count == 1


def test_log_error_when_api_return_an_error(
    mocker: MockerFixture, request_get: MockType
) -> None:
    payload_error = {
        "ok": False,
        "error_code": 400,
        "description": "Bad Request: chat not found",
    }
    request_get.return_value.json.return_value = payload_error
    logger_error = mocker.patch("spidermon.contrib.actions.telegram.logger.error")
    error_message = "Failed to send message. Telegram api error: %s"

    manager = TelegramMessageManager(sender_token="a-token", fake=False)
    manager.send_message(to=["1234"], text="Hello")

    assert logger_error.call_count == 1
    assert error_message == logger_error.call_args[0][0]
    assert json.dumps(payload_error) == logger_error.call_args[0][1]


def test_run_action_sends_message(mocker: MockerFixture) -> None:
    action = SendTelegramMessage(sender_token="token", recipients=["1234"])
    manager = action.manager = mocker.MagicMock()
    mocker.patch.object(action, "get_message", return_value="Hello")
    action.run_action()
    manager.send_message.assert_called_once_with(to=["1234"], text="Hello")


def test_spider_finished_notifier_settings(
    get_crawler: "Callable[..., Crawler]", mocker: MockerFixture
) -> None:
    crawler = get_crawler(
        {
            "SPIDERMON_TELEGRAM_SENDER_TOKEN": "token",
            "SPIDERMON_TELEGRAM_RECIPIENTS": ["1234"],
            "SPIDERMON_TELEGRAM_NOTIFIER_INCLUDE_OK_MESSAGES": True,
            "SPIDERMON_TELEGRAM_NOTIFIER_INCLUDE_ERROR_MESSAGES": False,
        }
    )
    kwargs = SendTelegramMessageSpiderFinished.from_crawler_kwargs(crawler)
    assert kwargs["include_ok_messages"] is True
    assert kwargs["include_error_messages"] is False

    action = SendTelegramMessageSpiderFinished(**kwargs)
    action.result = mocker.MagicMock()
    context = action.get_template_context()
    assert context["include_ok_messages"] is True
    assert context["include_error_messages"] is True
