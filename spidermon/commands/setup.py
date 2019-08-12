import click

from spidermon.commands.prompts import monitor_prompts
from spidermon.decorators.commands import is_inside_project
from spidermon.utils import monitors as monitors_manager
from spidermon.utils.commands import (
    build_monitors_strings,
    enable_spidermon,
    parse_int,
    parse_list,
    parse_dict,
    is_setting_setup,
    is_spidermon_enabled,
    is_valid,
    parse_user_input,
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
            settings += get_settings(module["monitors"][monitor])

    return monitors, settings


def get_settings(monitor):
    settings = []
    setting = monitor["setting"]
    name = monitor["name"]

    if is_setting_setup(setting):
        click.echo(monitor_prompts["setting_already_setup"].format(name))
        return settings

    setting_string = monitor["setting_string"]
    setting_type = monitor["setting_type"]
    description = monitor["description"]

    user_input = get_user_input(setting_type, description)
    if user_input:
        setting = setting_string.format(user_input)
        settings.append(setting)

    return settings


def get_user_input(setting_type, description):
    while True:
        user_input = []
        setting_types = []
        user_input += [click.prompt(monitor_prompts[setting_type].format(description))]
        setting_types += [setting_type]
        if setting_type == "dict":
            user_input += [click.prompt(monitor_prompts["list"].format(description))]
            setting_types += ["list"]

        if all(is_valid(a, b) for (a, b) in zip(user_input, setting_types)):
            return parse_user_input(user_input, setting_type)
        elif not click.confirm(monitor_prompts["setting_error"]):
            return []
