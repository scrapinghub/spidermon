from jinja2 import Environment, FileSystemLoader, BaseLoader


class TemplateLoader(object):
    def __init__(self):
        self.env = BaseLoader()
        self.paths = []

    def add_path(self, path):
        if path not in self.paths:
            self.paths.append(path)
            self.reload_env()

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
