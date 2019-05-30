from click import group
from .commands import version

@group('spidermon', help="Spidermon basic setup.")
def spidermon():
    ...

spidermon.add_command(version)

spidermon()
