from __future__ import absolute_import

import datetime
import inspect
import os
import pprint as pretty_print

import jinja2
from jinja2 import Environment, FileSystemLoader

DEFAULT_TEMPLATE_FOLDERS = ["templates"]


def get_log_errors(logs):
    return [e for e in logs.list() if e["level"] >= 40]


def make_list(obj):
    return list(obj)


def pprint(obj):
    return pretty_print.pformat(obj)


def format_time(time):
    if not isinstance(time, datetime.timedelta):
        time = datetime.timedelta(seconds=int(time / 1000.0))
    return ":".join(str(time).split(":")[:2]) + "h"


FILTERS = {
    "pprint": pprint,
    "list": make_list,
    "get_log_errors": get_log_errors,
    "format_time": format_time,
}
GLOBALS = {"datetime": datetime, "str": str}


def get_environment(paths):
    loader = FileSystemLoader(paths)
    environment = Environment(loader=loader, lstrip_blocks=True, trim_blocks=True)
    for filter_name, filter in FILTERS.items():
        environment.filters[filter_name] = filter

    for global_name, global_value in GLOBALS.items():
        environment.globals[global_name] = global_value

    return environment


class TemplateLoader(object):
    def __init__(self):
        self.paths = []
        self.reload_env()

    def add_path(self, path):
        if path not in self.paths and os.path.isdir(path):
            self.paths.append(path)
            self.reload_env()

    def auto_discover(self, path=None, folder=None):
        caller_folder = os.path.dirname(inspect.stack()[1][1])
        if path:
            caller_folder = os.path.join(caller_folder, path)
        if folder:
            self.add_path(os.path.join(caller_folder, folder))
        else:
            self.discover_folder(caller_folder)

    def discover_folder(self, candidate_folder):
        for folder in [
            os.path.join(candidate_folder, dir) for dir in DEFAULT_TEMPLATE_FOLDERS
        ]:
            self.add_path(folder)

    def reload_env(self):
        self.env = get_environment(self.paths)

    def get_template(self, name):
        if os.path.isabs(name):  # If provided an absolute path to a template
            environment = get_environment(os.path.dirname(name))
            template = environment.get_template(os.path.basename(name))
        else:
            template = self.env.get_template(name)
        return template


template_loader = TemplateLoader()
