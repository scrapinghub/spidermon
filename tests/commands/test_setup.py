from click.testing import CliRunner
from spidermon.commands import cli
from spidermon.commands.prompts import monitor_prompts

import pytest
import spidermon

@pytest.fixture
def cli(mocker):
    monitors = [{'Test': 'Foo'}]
    monitor_string_1 = 'Foo'
    monitor_string_2 = 'Bar'
    file = 'path/to/file'
    mocker.patch('scrapy.utils.project.inside_project', return_value=True)
    mocker.patch('spidermon.utils.commands.create_file', return_value=file)
    mocker.patch('spidermon.utils.commands.render_monitors')
    mocker.patch('spidermon.utils.commands.find_monitors', return_value=monitors)
    mocker.patch(
        'spidermon.utils.commands.build_monitors_strings',
        return_value=(monitor_string_1, monitor_string_2)
    )
    return cli


def test_should_fail_when_not_in_scrapy_project(cli):
    runner = CliRunner()
    result = runner.invoke(cli, ['setup'])
    assert result.exit_code == 0
    assert 'The command must be run inside a Scrapy project.' in result.output

def test_should_find_monitors_to_enable():
    runner = CliRunner()
    result = runner.invoke(cli, ['setup'])
    spidermon.utils.commands.find_monitors.assert_called_once()

def test_should_build_monitors_strings():
    runner = CliRunner()
    result = runner.invoke(cli, ['setup'])
    spidermon.utils.commands.build_monitors_strings.assert_called_once_with(
        monitors
    )

def test_should_create_suite_file_from_template():
    runner = CliRunner()
    result = runner.invoke(cli, ['setup'])
    spidermon.utils.commands.create_file.assert_called_once_with('monitor_suite.py.tmpl')

def test_should_render_monitor_suite():
    runner = CliRunner()
    result = runner.invoke(cli, ['setup'])
    spidermon.utils.commands.render_monitors.assert_called_once_with(
        file,
        monitor_string_1,
        monitor_string_2
    )
