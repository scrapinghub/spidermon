import click

from spidermon.commands.prompts import monitor_prompts
from spidermon.decorators.commands import is_inside_project
from spidermon.utils.commands import (
    build_monitors_strings,
    include_setting,
    is_setting_setup,
)
from spidermon.utils.file import copy_template_to_project, render_file
from spidermon.utils.monitors import find_monitor_modules


@click.command("setup", help="Setup the monitors from the Scrapy Monitor Suite.")
@is_inside_project
def setup():
    monitors = {}
    settings = []
    for module in find_monitor_modules():
        monitors.update(get_monitors(module))
        settings = [*settings, *get_settings(module, monitors)]

    monitors_list, imports = build_monitors_strings(monitors)
    filename = copy_template_to_project("monitor_suite.py.tmpl")

    include_setting(settings)
    render_file(filename, monitors_list=monitors_list, imports=imports)

    click.echo(monitor_prompts["response"])


def get_monitors(module):
    monitors = {}
    for monitor in module["monitors"]:
        msg = monitor_prompts["enable"].format(module["monitors"][monitor]["name"])
        if click.confirm(msg):
            monitors[monitor] = module["path"]

    return monitors


def get_settings(module, monitors):
    settings = []
    module_monitors = module["monitors"]
    for monitor in monitors:
        setting = module_monitors[monitor]["setting"]
        name = module_monitors[monitor]["name"]

        if is_setting_setup(setting):
            click.echo(monitor_prompts["setting_already_setup"].format(name))
            return

        setting_string = module_monitors[monitor]["setting_string"]
        categories = module_monitors[monitor]["categories"]
        description = module_monitors[monitor]["description"]
        entries = []

        for category in categories:
            entry = click.prompt(monitor_prompts[category].format(description))
            if category == "list":
                entry = entry.split(" ")
            entries.append(entry)

        if len(entries) == 2:
            entry = {code: int(entries[0]) for code in entries[1]}
        else:
            entry = entries[0]

        settings.append(setting_string.format(entry))

    return settings
