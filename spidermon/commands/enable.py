import click
import shutil
import string

from importlib import import_module
from os.path import abspath, dirname, join

import spidermon
from scrapy.utils.project import inside_project, get_project_settings
from spidermon.commands.prompts import monitor_prompts
from spidermon.utils.commands import check_settings, include_settings

@click.command('enable', help="Enable Spidermon on your Scrapy project.")
def enable():
    # check if it's inside a Scrapy project
    if not inside_project():
        click.echo('The command must be run inside a Scrapy project.')
        return

    # find settings file path
    module = import_module(get_project_settings().get('BOT_NAME'))
    settings_path = join(abspath(dirname(module.__file__)), 'settings.py')

    if check_settings(settings_path):
        include_settings(settings_path)
        click.echo(monitor_prompts['enable_result_true'])
    else:
        click.echo(monitor_prompts['enable_result_false'])
