from click import group
from .setup import setup
from .version import version


@group("spidermon", help="Spidermon basic setup.")
def cli():
    pass


cli.add_command(setup)
cli.add_command(version)
