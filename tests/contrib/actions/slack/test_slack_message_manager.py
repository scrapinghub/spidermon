import pytest

from scrapy.utils.test import get_crawler

from spidermon.contrib.actions.slack import SlackMessageManager, SendSlackMessage


@pytest.fixture
def logger_error(mocker):
    return mocker.patch("spidermon.contrib.actions.slack.logger.error")


@pytest.fixture
def mock_webclient(mocker):
    return mocker.patch("spidermon.contrib.actions.slack.WebClient")


@pytest.mark.parametrize("recipients", ["foo,bar", ["foo", "bar"]])
def test_load_recipients_list_from_crawler_settings(recipients):
    settings = {"SPIDERMON_SLACK_RECIPIENTS": recipients}
    crawler = get_crawler(settings_dict=settings)
    kwargs = SendSlackMessage.from_crawler_kwargs(crawler)
    assert kwargs["recipients"] == ["foo", "bar"]


def test_get_valid_icon_url(mock_webclient):
    mock_webclient().users_list.return_value = {
        "members": [{"name": "test_valid_user", "profile": {"image_48": "fake.jpg"}}]
    }
    manager = SlackMessageManager(sender_token="Fake", sender_name="test_valid_user")
    url = manager._get_icon_url()
    assert url == "fake.jpg"


def test_get_invalid_user_icon_url(mock_webclient):
    mock_webclient().users_list.return_value = {
        "members": [{"name": "test_valid_user", "profile": {"image_48": "fake.jpg"}}]
    }
    manager = SlackMessageManager(sender_token="Fake", sender_name="test_invalid_user")
    url = manager._get_icon_url()
    assert url is None
