import click

import spidermon
from scrapy.utils.project import inside_project
from spidermon.commands.prompts import monitor_prompts
from spidermon.utils.commands import build_monitors_strings, find_monitors
from spidermon.utils.file import copy_template_to_project, render_file

@click.command('setup', help="Setup the monitors from the Scrapy Monitor Suite.")
def setup():
    if not inside_project():
        click.echo(monitor_prompts['project_error'])
        return

    monitors_to_enable = {}
    for module in find_monitors():
        for monitor in module['monitors']:
            msg = monitor_prompts['enable'].format(module['monitors'][monitor])
            if click.confirm(msg):
                monitors_to_enable[monitor] = module['path']

    monitors_list, imports = build_monitors_strings(monitors_to_enable)

    filename = copy_template_to_project('monitor_suite.py.tmpl')
    render_file(filename, monitors_list=monitors_list, imports=imports)

    click.echo(monitor_prompts['response'])
