import click

from spidermon.commands.prompts import monitor_prompts
from spidermon.decorators.commands import is_inside_project
from spidermon.utils import monitors as monitors_manager
from spidermon.utils.commands import (
    build_monitors_strings,
    enable_spidermon,
    is_setting_setup,
    is_spidermon_enabled,
    update_settings,
)
from spidermon.utils import file_utils


@click.command(
    "setup",
    help="Enable Spidermon and setup the monitors from the Scrapy Monitor Suite.",
)
@is_inside_project
def setup():
    if is_spidermon_enabled():
        click.echo(monitor_prompts["already_enabled"])
    else:
        enable_spidermon()
        click.echo(monitor_prompts["enabled"])

    monitors = {}
    settings = []
    for module in monitors_manager.find_monitor_modules():
        new_monitors, new_settings = get_monitors_with_settings(module)
        monitors.update(new_monitors)
        settings += new_settings

    monitors_list, imports = build_monitors_strings(monitors)
    filename = file_utils.copy_template_to_project("monitor_suite.py.tmpl")

    if settings:
        update_settings(settings)
    file_utils.render_file(filename, monitors_list=monitors_list, imports=imports)

    click.echo(monitor_prompts["response"])


def get_monitors_with_settings(module):
    monitors = {}
    settings = []
    for monitor in module["monitors"]:
        msg = monitor_prompts["enable"].format(module["monitors"][monitor]["name"])
        if click.confirm("\n" + msg):
            monitors[monitor] = module["path"]
            settings += get_settings(module, module["monitors"][monitor])

    return monitors, settings


def get_setting(setting_string, setting_type, description):
    user_input = click.prompt(monitor_prompts[setting_type].format(description))
    if setting_type == "list":
        user_input = user_input.split(" ")
    if setting_type == "dict":
        items = click.prompt(monitor_prompts["list"].format(description))
        items = items.split(" ")
        user_input = {item: int(user_input) for item in items}

    return setting_string.format(user_input)


def get_settings(module, monitor):
    settings = []
    setting = monitor["setting"]
    name = monitor["name"]

    if is_setting_setup(setting):
        click.echo(monitor_prompts["setting_already_setup"].format(name))
        pass

    setting_string = monitor["setting_string"]
    setting_type = monitor["setting_type"]
    description = monitor["description"]

    settings.append(get_setting(setting_string, setting_type, description))

    return settings
