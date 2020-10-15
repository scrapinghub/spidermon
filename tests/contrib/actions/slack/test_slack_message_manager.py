import sys
import pytest

from scrapy.utils.test import get_crawler

from spidermon.contrib.actions.slack import SlackMessageManager, SendSlackMessage


@pytest.fixture
def logger_error(mocker):
    return mocker.patch("spidermon.contrib.actions.slack.logger.error")


@pytest.mark.parametrize("recipients", ["foo,bar", ["foo", "bar"]])
def test_load_recipients_list_from_crawler_settings(recipients):
    settings = {"SPIDERMON_SLACK_RECIPIENTS": recipients}
    crawler = get_crawler(settings_dict=settings)
    kwargs = SendSlackMessage.from_crawler_kwargs(crawler)
    assert kwargs["recipients"] == ["foo", "bar"]
