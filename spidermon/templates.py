import inspect
import os

from jinja2 import Environment, FileSystemLoader

DEFAULT_TEMPLATE_FOLDERS = ['templates']


class TemplateLoader(object):
    def __init__(self):
        self.paths = []
        self.reload_env()

    def add_path(self, path):
        if path not in self.paths and os.path.isdir(path):
            self.paths.append(path)
            self.reload_env()

    def auto_discover(self, folder=None):
        caller_folder = os.path.dirname(inspect.stack()[1][1])
        if folder:
            self.add_path(os.path.join(caller_folder, folder))
        else:
            self.discover_folder(caller_folder)

    def discover_folder(self, candidate_folder):
        for folder in [os.path.join(candidate_folder, dir)
                       for dir in DEFAULT_TEMPLATE_FOLDERS]:
            self.add_path(folder)

    def reload_env(self):
        loader = FileSystemLoader(self.paths)
        self.env = Environment(
            loader=loader,
            lstrip_blocks=True,
            trim_blocks=True,
            )

    def get_template(self, name):
        return self.env.get_template(name)

template_loader = TemplateLoader()
