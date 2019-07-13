from click.testing import CliRunner
from spidermon.commands import cli
from spidermon.commands.prompts import monitor_prompts
from spidermon.utils.monitors import find_monitor_modules

from unittest.mock import MagicMock
from pytest_mock import mocker

import pytest
import spidermon


@pytest.fixture()
def runner():
    runner = CliRunner()
    yield runner.isolated_filesystem()


def test_should_notify_success_on_spidermon_enabled(runner):
    result = runner.invoke(cli, ["setup"])
    assert result.exit_code == 0
    assert result.output == monitor_prompts["enabled"]


def test_should_notify_that_spidermon_was_already_enabled(runner):
    result = runner.invoke(cli, ["setup"])
    assert result.exit_code == 0
    assert result.output == monitor_prompts["already_enabled"]


def test_should_ask_monitors_to_enable():
    mocker.patch.object(spidermon.utils.monitors, "find_monitor_modules")
    result = runner.invoke(cli, ["setup"])
    assert result.exit_code == 0


def test_should_ask_settings_from_monitors_to_enable():
    ...
