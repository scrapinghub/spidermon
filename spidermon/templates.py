import datetime
import inspect
import pprint as pretty_print
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

DEFAULT_TEMPLATE_FOLDERS = ["templates"]
LOG_ERROR_LEVEL = 40


def get_log_errors(logs):
    return [e for e in logs.list() if e["level"] >= LOG_ERROR_LEVEL]


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
    environment = Environment(loader=loader, lstrip_blocks=True, trim_blocks=True)  # noqa: S701
    for filter_name, filter_ in FILTERS.items():
        environment.filters[filter_name] = filter_

    for global_name, global_value in GLOBALS.items():
        environment.globals[global_name] = global_value

    return environment


class TemplateLoader:
    def __init__(self):
        self.paths = []
        self.reload_env()

    def add_path(self, path):
        if str(path) not in self.paths and Path(path).is_dir():
            self.paths.append(str(path))
            self.reload_env()

    def auto_discover(self, path=None, folder=None):
        caller_folder = Path(inspect.stack()[1][1]).parent
        if path:
            caller_folder = caller_folder / path
        if folder:
            self.add_path(str(caller_folder / folder))
        else:
            self.discover_folder(str(caller_folder))

    def discover_folder(self, candidate_folder):
        for folder in [
            str(Path(candidate_folder) / subfolder)
            for subfolder in DEFAULT_TEMPLATE_FOLDERS
        ]:
            self.add_path(folder)

    def reload_env(self):
        self.env = get_environment(self.paths)

    def get_template(self, name):
        if Path(name).is_absolute():  # If provided an absolute path to a template
            environment = get_environment(str(Path(name).parent))
            template = environment.get_template(Path(name).name)
        else:
            template = self.env.get_template(str(name))
        return template


template_loader = TemplateLoader()
