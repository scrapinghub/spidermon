import shutil
import string

from importlib import import_module
from os.path import abspath, dirname, join
from scrapy.utils.project import get_project_settings

import spidermon


def copy_template_to_project(template):
    template_file = join(spidermon.__path__[0], "templates", template)
    module = import_module(get_project_settings().get("BOT_NAME"))
    module_dir = abspath(dirname(module.__file__))
    monitors_file = join(module_dir, "monitors.py")
    shutil.copyfile(template_file, monitors_file)
    return monitors_file


def render_file(filename, **kwargs):
    with open(filename, "r") as f:
        raw = f.read()

    content = string.Template(raw).substitute(**kwargs)

    with open(filename.rstrip(".tmpl"), "w") as f:
        f.write(content)
