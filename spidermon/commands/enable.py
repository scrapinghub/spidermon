import click
import shutil
import string

from importlib import import_module
from os.path import abspath, dirname, join

import spidermon
from scrapy.utils.project import inside_project, get_project_settings
from spidermon.commands.prompts import monitor_prompts
from spidermon.commands.settings import monitor_settings
from spidermon.utils.commands import include_settings

@click.command('enable', help="Enable Spidermon on your Scrapy project.")
def enable():
    # check if it's inside a Scrapy project
    if inside_project():
        ...
    else:
        click.echo('The command must be run inside a Scrapy project.')
        return

    result = include_settings(monitor_settings)

    if result:
        click.echo(monitor_prompts['enable_result_true'])
    else:
        click.echo(monitor_prompts['enable_result_false'])
