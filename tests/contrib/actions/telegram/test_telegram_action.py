import pytest

from spidermon.contrib.actions.telegram import TelegramMessageManager


@pytest.fixture
def logger_info(mocker):
    return mocker.patch("spidermon.contrib.actions.telegram.logger.info")


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
