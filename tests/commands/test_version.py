from click.testing import CliRunner
from spidermon.commands import cli

import spidermon

def test_should_echo_current_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['version'])
    assert result.exit_code == 0
    assert 'Spidermon %s' % spidermon.__version__ in result.output
