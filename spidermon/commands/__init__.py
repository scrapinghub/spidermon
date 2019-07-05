from click import group
from .enable import enable
from .setup import setup
from .version import version


@group("spidermon", help="Spidermon basic setup.")
def cli():
    ...


cli.add_command(enable)
cli.add_command(setup)
cli.add_command(version)
