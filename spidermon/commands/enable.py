import click

from spidermon.commands.prompts import monitor_prompts
from spidermon.decorators.commands import is_inside_project
from spidermon.utils.commands import is_spidermon_enabled, enable_spidermon


@click.command("enable", help="Enable Spidermon on your Scrapy project.")
@is_inside_project
def enable():
    if is_spidermon_enabled():
        click.echo(monitor_prompts["already_enabled"])
    else:
        enable_spidermon()
        click.echo(monitor_prompts["enabled"])
