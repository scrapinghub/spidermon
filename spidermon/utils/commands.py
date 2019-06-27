from importlib import import_module
from os.path import abspath, dirname, join
from scrapy.utils.project import get_project_settings

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

def include_settings(settings_list):
    # find and open settings file
    module = import_module(get_project_settings().get('BOT_NAME'))
    settings_file = join(abspath(dirname(module.__file__)), 'settings.py')
    with open(settings_file, 'r') as f:
        read_data = f.read()

        # check if spidermon was already enabled
        for setting in settings_list:
            if setting in read_data:
                return False

    with open(settings_file, 'a') as f:
        f.writelines('\n'.join(settings_list))

    return True
