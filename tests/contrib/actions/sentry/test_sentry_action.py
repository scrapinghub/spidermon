from types import SimpleNamespace

import pytest

pytest.importorskip("scrapy")
pytest.importorskip("sentry_sdk")

from spidermon.contrib.actions.sentry import SendSentryMessage
from spidermon.data import Data
from spidermon.exceptions import NotConfigured


def make_monitor_result(name, error):
    return SimpleNamespace(monitor=SimpleNamespace(name=name), error=error)


@pytest.fixture
def logger_info(mocker):
    return mocker.patch("spidermon.contrib.actions.sentry.logger.info")


@pytest.fixture
def sentry_client(mocker):
    return mocker.patch("spidermon.contrib.actions.sentry.Client")


@pytest.fixture
def scope(mocker):
    configure_scope = mocker.patch("spidermon.contrib.actions.sentry.configure_scope")
    return configure_scope.return_value.__enter__.return_value


@pytest.fixture
def action():
    action = SendSentryMessage(
        sentry_dsn="https://key@example.com/1",
        project_name="my-project",
        environment="Production",
    )
    action.data = Data(
        spider=None,
        job=None,
        stats=None,
        sc_spider_name="my-spider",
    )
    action.result = None
    return action


def test_fail_if_no_dsn():
    with pytest.raises(NotConfigured):
        SendSentryMessage(project_name="my-project")


def test_fail_if_no_project_name():
    with pytest.raises(NotConfigured):
        SendSentryMessage(sentry_dsn="https://key@example.com/1")


def test_dsn_not_required_when_fake():
    action = SendSentryMessage(fake=True, project_name="my-project")
    assert action.sentry_dsn is None


def test_defaults_used_when_no_arguments_given():
    class ConfiguredSentryMessage(SendSentryMessage):
        sentry_dsn = "https://key@example.com/1"
        project_name = "class-project"
        environment = "Staging"
        sentry_log_level = "warning"

    action = ConfiguredSentryMessage()

    assert action.sentry_dsn == "https://key@example.com/1"
    assert action.project_name == "class-project"
    assert action.environment == "Staging"
    assert action.sentry_log_level == "warning"
    assert action.fake is False


def test_from_crawler_kwargs(get_crawler):
    crawler = get_crawler(
        {
            "SPIDERMON_SENTRY_DSN": "https://key@example.com/1",
            "SPIDERMON_SENTRY_FAKE": True,
            "SPIDERMON_SENTRY_LOG_LEVEL": "warning",
            "SPIDERMON_SENTRY_PROJECT_NAME": "my-project",
            "SPIDERMON_SENTRY_ENVIRONMENT_TYPE": "Production",
        },
    )

    action = SendSentryMessage.from_crawler(crawler)

    assert action.sentry_dsn == "https://key@example.com/1"
    assert action.fake is True
    assert action.sentry_log_level == "warning"
    assert action.project_name == "my-project"
    assert action.environment == "Production"


def test_run_action_logs_message_when_fake(logger_info, sentry_client):
    action = SendSentryMessage(fake=True, project_name="my-project")
    action.data = Data(
        spider=None,
        job=None,
        stats=None,
        sc_spider_name="my-spider",
    )
    action.result = None

    action.run_action()

    assert logger_info.call_args[0][0]["title"] == action.get_title()
    assert sentry_client.call_count == 0


def test_run_action_sends_message_when_not_fake(action, mocker):
    send_message = mocker.patch.object(action, "send_message")

    action.run_action()

    send_message.assert_called_once_with(action.get_message())


def test_get_title(action):
    action.data = Data(sc_spider_name="my-spider")

    assert (
        action.get_title() == "my-project | Production | Spider my-spider notification"
    )


def test_get_message_without_data_or_result(action):
    assert action.get_message() == {"title": action.get_title()}


def test_get_message_with_data(action):
    action.data = Data(
        spider=object(),
        job=SimpleNamespace(key="123/4/5"),
        stats={"item_scraped_count": 42},
        sc_spider_name="my-spider",
    )

    message = action.get_message()

    assert message["job_link"] == "https://app.zyte.com/p/123/4/5"
    assert message["spider_name"] == "my-spider"
    assert message["items_count"] == 42


def test_get_message_defaults_items_count_to_zero(action):
    action.data = Data(
        spider=None,
        job=None,
        stats={"other_stat": 1},
        sc_spider_name="my-spider",
    )

    assert action.get_message()["items_count"] == 0


def test_get_message_with_result(action, mocker):
    action.result = mocker.MagicMock(
        monitors_passed_results=[make_monitor_result("passed", None)],
        monitors_failed_results=[
            make_monitor_result("Monitor/failed one", "first reason"),
            make_monitor_result("Monitor/failed two", "second reason"),
        ],
    )

    message = action.get_message()

    assert message["passed_monitors_count"] == 1
    assert message["failed_monitors_count"] == 2
    assert message["failed_monitors"] == ["Monitor/failed one", "Monitor/failed two"]
    assert message["failure_reasons"] == "first reason\nsecond reason"


def test_get_tags(action):
    tags = action.get_tags(
        {"spider_name": "my-spider", "failed_monitors": ["Monitor/Failed Monitor"]},
    )

    assert tags == {
        "spider_name": "my-spider",
        "project_name": "my-project",
        "failed_monitor": 1,
    }


def test_get_tags_without_message_contents(action):
    assert action.get_tags({}) == {"spider_name": "", "project_name": "my-project"}


def test_get_tags_truncates_long_monitor_names(action):
    tags = action.get_tags({"failed_monitors": ["a" * 40]})

    assert "a" * 32 in tags


def test_send_message(action, sentry_client, scope, logger_info):
    action.send_message(
        {
            "title": "the title",
            "failure_reasons": "the reasons",
            "spider_name": "my-spider",
            "job_link": "https://app.zyte.com/p/123/4/5",
            "items_count": 42,
            "passed_monitors_count": 1,
            "failed_monitors_count": 2,
            "failed_monitors": ["Monitor/failed"],
        },
    )

    sentry_client.assert_called_once_with(
        dsn="https://key@example.com/1",
        environment="Production",
    )
    event = sentry_client.return_value.capture_event.call_args.kwargs["event"]
    assert event["message"] == "the title \n the reasons"
    assert event["level"] == "error"
    assert event["fingerprint"] == ["the title"]
    assert sentry_client.return_value.close.call_count == 1
    assert logger_info.call_count == 1


def test_send_message_sets_scope(action, sentry_client, scope, mocker):
    action.send_message({"title": "the title", "spider_name": "my-spider"})

    assert mocker.call("spider_name", "my-spider") in scope.set_tag.call_args_list
    assert mocker.call("project_name", "my-project") in scope.set_tag.call_args_list
    assert mocker.call("items_count", 0) in scope.set_extra.call_args_list
    assert mocker.call("failed_monitors", []) in scope.set_extra.call_args_list
