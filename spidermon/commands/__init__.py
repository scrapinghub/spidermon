from click import group
from .version import version

@group('spidermon', help="Spidermon basic setup.")
def cli():
    ...

cli.add_command(version)
