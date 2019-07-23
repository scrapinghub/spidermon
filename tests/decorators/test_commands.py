from spidermon.commands.prompts import monitor_prompts
from spidermon.decorators import commands

from io import StringIO
from pytest_mock import mocker
from unittest.mock import patch, Mock

import click
import pytest
import spidermon


@commands.is_inside_project
def fun():
    ...


@pytest.fixture
def mocker(mocker):
    mocker.patch.object(commands, "inside_project")
    mocker.patch("click.echo")
    return mocker


def test_should_notify_when_not_inside_scrapy_project(mocker):
    commands.inside_project.return_value = False
    mock_fun = Mock()
    fun()
    click.echo.assert_called_with(monitor_prompts["project_error"])
