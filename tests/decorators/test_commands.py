from spidermon.commands.prompts import monitor_prompts
from spidermon.decorators import commands

from io import StringIO
from pytest_mock import mocker
from unittest.mock import patch, Mock

import click
import pytest
import spidermon


@pytest.fixture
def mocker(mocker):
    mocker.patch.object(commands, "inside_project")
    mocker.patch("click.echo")
    return mocker


def test_should_call_decorated_function_with_arguments(mocker):
    commands.inside_project.return_value = True

    mock = Mock()
    decorated = commands.is_inside_project(mock)
    decorated("argument")

    mock.assert_called_with("argument")


def test_should_call_decorated_function_with_multiple_arguments(mocker):
    commands.inside_project.return_value = True

    mock = Mock()
    decorated = commands.is_inside_project(mock)
    decorated("argument", "another argument")

    mock.assert_called_with("argument", "another argument")


def test_should_call_decorated_function_when_inside_scrapy_project(mocker):
    commands.inside_project.return_value = True

    mock = Mock()
    decorated = commands.is_inside_project(mock)
    decorated()

    mock.assert_called()


def test_should_notify_when_not_inside_scrapy_project(mocker):
    commands.inside_project.return_value = False

    mock = Mock()
    decorated = commands.is_inside_project(mock)
    decorated()

    click.echo.assert_called_with(monitor_prompts["project_error"])
    mock.assert_not_called()
