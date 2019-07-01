import click

from scrapy.utils.project import inside_project
from spidermon.commands.prompts import monitor_prompts
from spidermon.utils.commands import is_spidermon_enabled, enable_spidermon

@click.command('enable', help="Enable Spidermon on your Scrapy project.")
def enable():
    if not inside_project():
        click.echo(monitor_prompts['project_error'])
        return

    if is_spidermon_enabled():
        click.echo(monitor_prompts['already_enabled'])
    else:
        enable_spidermon()
        click.echo(monitor_prompts['enabled'])
