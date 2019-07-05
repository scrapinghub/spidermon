import click

import spidermon


@click.command("version", help="Print Spidermon version.")
def version():
    click.echo("Spidermon %s" % spidermon.__version__)
