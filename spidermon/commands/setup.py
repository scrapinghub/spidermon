import click

import spidermon
from scrapy.utils.project import inside_project
from spidermon.commands.prompts import monitor_prompts
from spidermon.utils.commands import build_monitors_strings, find_monitors
from spidermon.utils.file import create_file, render_file

@click.command('setup', help="Setup the monitors from the Scrapy Monitor Suite.")
def setup():
    # check if it's inside a Scrapy project
    if not inside_project():
        click.echo(monitor_prompts['project_error'])
        return

    # build string with monitors to be enabled
    monitors = find_monitors()
    monitors_to_enable = {}
    for module in monitors:
        for monitor in module['monitors']:
            result = click.confirm(
                monitor_prompts['enable'].format(module['monitors'][monitor])
            )
            if result:
                monitors_to_enable[monitor] = module['path']
    monitors_list, monitors_imports = build_monitors_strings(
        monitors_to_enable
    )

    # create and build file with monitors
    filename = create_file('monitor_suite.py.tmpl')
    render_file(
        filename,
        monitors_list=monitors_list,
        monitors_imports=monitors_imports
    )

    click.echo(monitor_prompts['response'])
