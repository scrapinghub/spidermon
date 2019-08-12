from click.testing import CliRunner
from pytest_mock import mocker
from scrapy.settings import Settings
from spidermon.commands import cli
from spidermon.commands.prompts import monitor_prompts
from spidermon.commands.setup import get_settings, get_user_input
from spidermon.decorators import commands as decorator_commands
from spidermon.utils import commands, file_utils, monitors

import click
import pytest
import spidermon
import time

SETTING_DESCRIPTION = "test items"
SETTING_STRING = "TEST_SETTING = {}"
SETTING_TYPE_DICT = "dict"
SETTING_TYPE_LIMIT_LEAST = "limit_least"
SETTING_TYPE_LIMIT_MOST = "limit_most"
SETTING_TYPE_LIST = "list"

MODULE_MONITORS = {"TestMonitor": "path.to.monitor"}
MODULE_MONITOR_LIST = [
    {
        "path": "path.to.monitor",
        "monitors": {
            "TestMonitor": {
                "name": "Test",
                "setting": "TEST_SETTING",
                "setting_string": SETTING_STRING,
                "description": SETTING_DESCRIPTION,
                "setting_type": SETTING_TYPE_LIMIT_LEAST,
            }
        },
    }
]
TEST_MONITOR = {
    "name": "Test",
    "setting": "TEST_SETTING",
    "setting_string": SETTING_STRING,
    "description": SETTING_DESCRIPTION,
    "setting_type": SETTING_TYPE_LIMIT_LEAST,
}
PROJECT_SETTINGS = Settings(values={"BOT_NAME": "test_bot"})
PROJECT_SETTINGS_WITH_SPIDERMON = Settings(
    values={"BOT_NAME": "test_bot", "SPIDERMON_ENABLED": True}
)
PROJECT_SETTINGS_WITH_SETTING = Settings(
    values={"BOT_NAME": "test_bot", "TEST_SETTING": 1}
)


@pytest.fixture
def mocker_commands(mocker):
    mocker.patch.object(commands, "build_monitors_strings")
    mocker.patch.object(commands, "enable_spidermon")
    mocker.patch.object(commands, "get_project_settings")
    mocker.patch.object(commands, "get_settings_path")
    mocker.patch.object(commands, "is_setting_setup")
    mocker.patch.object(commands, "update_settings")
    mocker.patch.object(decorator_commands, "inside_project")
    mocker.patch.object(file_utils, "copy_template_to_project")
    mocker.patch.object(file_utils, "render_file")
    mocker.patch.object(monitors, "find_monitor_modules")

    commands.get_project_settings.return_value = PROJECT_SETTINGS
    commands.is_setting_setup.return_value = False
    decorator_commands.inside_project.return_value = True
    monitors.find_monitor_modules.return_value = MODULE_MONITOR_LIST

    return mocker


@pytest.fixture
def mocker_click(mocker):
    mocker.patch.object(click, "prompt")
    mocker.patch.object(click, "echo")
    mocker.patch.object(click, "confirm")

    return mocker


@pytest.fixture
def runner():
    runner = CliRunner()
    return runner


def test_should_notify_when_not_in_scrapy_project(mocker_commands, runner):
    decorator_commands.inside_project.return_value = False
    result = runner.invoke(cli, ["setup"])
    assert result.exit_code == 0
    assert (monitor_prompts["project_error"] + "\n") in result.output


def test_should_notify_success_on_spidermon_enabled(mocker_commands, runner):
    result = runner.invoke(cli, ["setup"])
    assert result.exit_code == 0
    assert (monitor_prompts["enabled"] + "\n") in result.output


def test_should_notify_that_spidermon_was_already_enabled(mocker_commands, runner):
    commands.get_project_settings.return_value = PROJECT_SETTINGS_WITH_SPIDERMON
    commands.is_setting_setup.return_value = True

    result = runner.invoke(cli, ["setup"])
    assert result.exit_code == 0
    assert (monitor_prompts["already_enabled"] + "\n") in result.output


def test_should_ask_monitors_to_enable(mocker_commands, runner):
    result = runner.invoke(cli, ["setup"])
    expected_output = monitor_prompts["enable"].format("Test")
    assert result.exit_code == 0
    assert expected_output in result.output


def test_should_notify_when_monitor_setting_already_exists(
    mocker_click, mocker_commands
):
    commands.get_project_settings.return_value = PROJECT_SETTINGS_WITH_SETTING
    expected_output = monitor_prompts["setting_already_setup"].format("Test")

    result = get_settings(TEST_MONITOR)

    assert not result
    click.echo.assert_called_with(expected_output)


def test_should_return_list_of_settings(mocker_click, mocker_commands):
    click.prompt.return_value = "10"
    click.confirm.return_value = False
    expected_setting_string = SETTING_STRING.format(10)
    assert get_settings(TEST_MONITOR) == [expected_setting_string]


@pytest.mark.parametrize("input", ["-10", "foo, bar"])
def test_should_return_empty_list_of_settings_for_invalid_input(
    mocker_click, mocker_commands, input
):
    click.prompt.return_value = input
    click.confirm.return_value = False
    assert get_settings(TEST_MONITOR) == []


@pytest.mark.parametrize(
    "input, setting_type, description",
    [
        ("10", SETTING_TYPE_LIMIT_MOST, SETTING_DESCRIPTION),
        ("20", SETTING_TYPE_LIMIT_LEAST, SETTING_DESCRIPTION),
        ("foo, bar, baz", SETTING_TYPE_LIST, SETTING_DESCRIPTION),
    ],
)
def test_should_ask_setting_value(mocker_click, input, setting_type, description):
    click.prompt.return_value = input
    click.confirm.return_value = False
    get_user_input(setting_type, description)
    click.prompt.assert_called_with(monitor_prompts[setting_type].format(description))


def test_should_ask_twice_for_dict(mocker_click):
    click.prompt.return_value = "10"
    get_user_input(SETTING_TYPE_DICT, SETTING_DESCRIPTION)
    calls = [
        mocker_click.call(
            monitor_prompts[SETTING_TYPE_DICT].format(SETTING_DESCRIPTION)
        ),
        mocker_click.call(
            monitor_prompts[SETTING_TYPE_LIST].format(SETTING_DESCRIPTION)
        ),
    ]
    click.prompt.assert_has_calls(calls)


@pytest.mark.parametrize(
    "setting_type, description, user_input",
    [
        (SETTING_TYPE_LIMIT_LEAST, SETTING_DESCRIPTION, "-10"),
        (SETTING_TYPE_LIMIT_MOST, SETTING_DESCRIPTION, "-20"),
        (SETTING_TYPE_LIST, SETTING_DESCRIPTION, ""),
        (SETTING_TYPE_DICT, SETTING_DESCRIPTION, "-30"),
    ],
)
def test_should_return_empty_list_when_stop_retrying(
    mocker_click, setting_type, description, user_input
):
    click.confirm.return_value = False
    click.prompt.return_value = user_input
    assert get_user_input(setting_type, description) == []


@pytest.mark.parametrize(
    "setting_type, description, user_input",
    [
        (SETTING_TYPE_LIMIT_LEAST, SETTING_DESCRIPTION, "-10"),
        (SETTING_TYPE_LIMIT_MOST, SETTING_DESCRIPTION, "-20"),
        (SETTING_TYPE_LIST, SETTING_DESCRIPTION, ""),
        (SETTING_TYPE_DICT, SETTING_DESCRIPTION, "-30"),
    ],
)
def test_should_notify_when_invalid_input(
    mocker_click, setting_type, description, user_input
):
    click.confirm.return_value = False
    click.prompt.return_value = user_input
    get_user_input(setting_type, description)
    click.confirm.assert_called_with(monitor_prompts["setting_error"])


@pytest.mark.parametrize(
    "setting_type, description, user_input",
    [
        (SETTING_TYPE_LIMIT_LEAST, SETTING_DESCRIPTION, "-10"),
        (SETTING_TYPE_LIMIT_MOST, SETTING_DESCRIPTION, "-20"),
        (SETTING_TYPE_LIST, SETTING_DESCRIPTION, ""),
        (SETTING_TYPE_DICT, SETTING_DESCRIPTION, "-30"),
    ],
)
def test_should_retry_if_user_allows(
    mocker_click, setting_type, description, user_input
):
    click.confirm.side_effect = [True, True, False]
    click.prompt.return_value = user_input
    get_user_input(setting_type, description)
    assert click.confirm.call_count == 3


@pytest.mark.parametrize(
    "setting_type, description, user_input",
    [
        (SETTING_TYPE_LIMIT_LEAST, SETTING_DESCRIPTION, "-10"),
        (SETTING_TYPE_LIMIT_MOST, SETTING_DESCRIPTION, "-20"),
        (SETTING_TYPE_LIST, SETTING_DESCRIPTION, ""),
        (SETTING_TYPE_DICT, SETTING_DESCRIPTION, "-30"),
    ],
)
def test_should_not_retry_if_user_denies(
    mocker_click, setting_type, description, user_input
):
    click.confirm.return_value = False
    click.prompt.return_value = user_input
    get_user_input(setting_type, description)
    click.confirm.assert_called_once()


@pytest.mark.parametrize(
    "value, keys, setting_type, description",
    [
        (10, "", "dict", SETTING_DESCRIPTION),
        (-20, "foo, bar, baz", "dict", SETTING_DESCRIPTION),
    ],
)
def test_should_validate_all_dict_inputs(
    mocker_click, value, keys, setting_type, description
):
    click.prompt.side_effect = [keys, value]
    click.confirm.return_value = False
    result = get_user_input(setting_type, description)
    click.confirm.assert_called_once()
    assert not result
