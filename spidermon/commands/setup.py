import click

from importlib import import_module

import spidermon
from scrapy.utils.project import inside_project
from spidermon.commands.prompts import monitor_prompts
from spidermon.utils.commands import build_monitors_strings, include_setting, is_setting_setup
from spidermon.utils.file import copy_template_to_project, render_file
from spidermon.utils.monitors import find_monitors

@click.command('setup', help="Setup the monitors from the Scrapy Monitor Suite.")
def setup():
    if not inside_project():
        click.echo(monitor_prompts['project_error'])
        return

    monitors = {}
    settings = []
    for module in find_monitors():
        monitors, settings = handle_monitors(module)

    monitors_list, imports = build_monitors_strings(monitors)
    filename = copy_template_to_project('monitor_suite.py.tmpl')

    include_setting(settings)
    render_file(filename, monitors_list=monitors_list, imports=imports)

    click.echo(monitor_prompts['response'])

def handle_monitors(module):
    monitors = {}
    settings = []
    for monitor in module['monitors']:
        msg = monitor_prompts['enable'].format(module['monitors'][monitor]['name'])
        if click.confirm(msg):
            monitors[monitor] = module['path']
            setting = handle_settings(module['monitors'][monitor])
            if setting:
                settings.append(setting)

    return monitors, settings

def handle_settings(monitor):
    setting = monitor['setting']
    name = monitor['name']

    if is_setting_setup(setting):
        click.echo(monitor_prompts['setting_already_setup'].format(name))
        return

    setting_string = monitor['setting_string']
    types = monitor['types']
    description = monitor['description']
    inputs = []

    for type in types:
        input = click.prompt(monitor_prompts[type].format(description))
        if type is 'list':
            input = input.split(' ')
        inputs.append(input)

    if len(inputs) is 2:
        input = { code: int(inputs[0]) for code in inputs[1] }
    else:
        input = inputs[0]

    return setting_string.format(input)
