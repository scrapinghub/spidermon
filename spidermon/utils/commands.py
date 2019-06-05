import click
import shutil
import string

from importlib import import_module
from os.path import abspath, dirname, join
from scrapy.utils.project import get_project_settings

from spidermon.commands.prompts import monitor_prompts

import spidermon

def build_monitors_strings(monitors):
    monitors_list = '['
    monitors_import = ''
    for monitor in monitors:
        monitors_list += monitor + ','
        monitors_import += 'from {} import {}\n'.format(
            monitors[monitor],
            monitor
        )
    monitors_list += ']'

    return monitors_list, monitors_import

def create_file(template):
    template_file = join(spidermon.__path__[0], 'templates', template)
    module = import_module(get_project_settings().get('BOT_NAME'))
    module_dir = abspath(dirname(module.__file__))
    monitors_file = join(module_dir, 'monitors.py')
    shutil.copyfile(template_file, monitors_file)
    return monitors_file

def find_monitors():
    return [{
        'path': 'spidermon.contrib.scrapy.monitors',
        'monitors': {
            'ItemCountMonitor': 'Item Count Monitor',
            'ErrorCountMonitor': 'Error Count Monitor',
            'FinishReasonMonitor': 'Finish Reason Monitor',
            'UnwantedHTTPCodesMonitor': 'Unwanted HTTP Code Monitor',
        }
    }]

def render_monitors(monitors_file, monitors_list, monitors_imports):
    with open(monitors_file, 'r') as file:
        raw = file.read()

    content = string.Template(raw).substitute(
        monitors_imports=monitors_imports,
        monitors_list=monitors_list
    )

    with open(monitors_file.rstrip('.tmpl'), 'w') as file:
        file.write(content)
