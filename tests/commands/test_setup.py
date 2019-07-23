from click.testing import CliRunner
from pytest_mock import mocker
from scrapy.settings import Settings
from spidermon.commands import cli
from spidermon.commands.prompts import monitor_prompts
from spidermon.commands.setup import get_setting, get_settings
from spidermon.decorators import commands as decorator_commands
from spidermon.utils import commands, file_utils, monitors
from unittest.mock import MagicMock

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
                "name": "Test Monitor",
                "setting": "TEST_SETTING",
                "setting_string": SETTING_STRING,
                "description": SETTING_DESCRIPTION,
                "setting_type": SETTING_TYPE_LIMIT_LEAST,
            }
        },
    }
]
PROJECT_SETTINGS = Settings()
PROJECT_SETTINGS.setdict({"BOT_NAME": "test_bot"})
PROJECT_SETTINGS_WITH_SPIDERMON = Settings()
PROJECT_SETTINGS_WITH_SPIDERMON.setdict(
    {"BOT_NAME": "test_bot", "SPIDERMON_ENABLED": True}
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

    result = runner.invoke(cli, ["setup"])
    assert result.exit_code == 0
    assert (monitor_prompts["already_enabled"] + "\n") in result.output


def test_should_ask_monitors_to_enable(mocker_commands, runner):
    result = runner.invoke(cli, ["setup"])
    expected_output = monitor_prompts["enable"].format(
        MODULE_MONITOR_LIST[0]["monitors"]["TestMonitor"]["name"]
    )
    assert result.exit_code == 0
    assert expected_output in result.output


def test_should_get_settings(mocker_click, runner):
    expected_output = monitor_prompts["limit_least"].format(
        MODULE_MONITOR_LIST[0]["monitors"]["TestMonitor"]["description"]
    )

    get_setting(SETTING_STRING, SETTING_TYPE_LIMIT_LEAST, SETTING_DESCRIPTION)

    click.prompt.assert_called_with(expected_output)


def test_should_ask_setting_from_monitors_to_enable_when_limit_least(
    mocker_click, runner
):
    expected_output = monitor_prompts["limit_least"].format(
        MODULE_MONITOR_LIST[0]["monitors"]["TestMonitor"]["description"]
    )

    get_setting(SETTING_STRING, SETTING_TYPE_LIMIT_LEAST, SETTING_DESCRIPTION)

    click.prompt.assert_called_with(expected_output)


def test_should_ask_setting_from_monitors_to_enable_when_limit_most(
    mocker_click, runner
):
    expected_output = monitor_prompts["limit_most"].format(
        MODULE_MONITOR_LIST[0]["monitors"]["TestMonitor"]["description"]
    )

    get_setting(SETTING_STRING, SETTING_TYPE_LIMIT_MOST, SETTING_DESCRIPTION)

    click.prompt.assert_called_with(expected_output)


def test_should_ask_setting_from_monitors_to_enable_when_list(mocker_click, runner):
    expected_output = monitor_prompts["list"].format(
        MODULE_MONITOR_LIST[0]["monitors"]["TestMonitor"]["description"]
    )

    get_setting(SETTING_STRING, SETTING_TYPE_LIST, SETTING_DESCRIPTION)

    click.prompt.assert_called_with(expected_output)


def test_should_ask_setting_from_monitors_to_enable_when_dict(mocker_click, runner):
    expected_output_dict = monitor_prompts["dict"].format(SETTING_DESCRIPTION)
    expected_output_list = monitor_prompts["list"].format(SETTING_DESCRIPTION)

    get_setting(SETTING_STRING, SETTING_TYPE_DICT, SETTING_DESCRIPTION)

    click.prompt.assert_any_call(expected_output_dict)
    click.prompt.assert_any_call(expected_output_list)
    assert click.prompt.call_count == 2
