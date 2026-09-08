import inspect
from pathlib import Path
from typing import Any, ClassVar

from jinja2 import Template

from spidermon.core.actions import Action
from spidermon.core.options import ActionOptionsMetaclass
from spidermon.templates import template_loader


class ActionWithTemplatesMetaclass(ActionOptionsMetaclass):
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        mcs.add_class_templates(cls)
        return cls

    @classmethod
    def add_class_templates(mcs, cls):
        class_file = inspect.getfile(cls)
        class_path = Path(class_file).parent
        template_loader.discover_folder(str(class_path))
        for path in cls.template_paths:
            template_path = class_path / path
            template_loader.add_path(str(template_path))


class ActionWithTemplates(Action, metaclass=ActionWithTemplatesMetaclass):
    template_paths: ClassVar[list[str]] = []
    context: dict[str, Any] | None = None

    def __init__(self, context=None):
        super().__init__()
        self.context = context or self.context or {}

    def get_template(self, name):
        return template_loader.get_template(name)

    def render_text_template(self, template):
        """Render a Jinja2 template given in *template* as a string.

        For example::

            action.render_text_template('{{ monitors_failed }} monitors failed!')
        """
        template = Template(template)
        return template.render(self.get_template_context())

    def render_template(self, template):
        """Render the Jinja2 template file named *template*.

        It uses :data:`spidermon.templates.template_loader` to resolve
        *template* to an actual template file.

        For example::

            action.render_template('mytemplate.html')
        """
        template = self.get_template(template)
        return template.render(self.get_template_context())

    def get_template_context(self):
        context = {
            "result": self.result,
            "data": self.data,
            "monitors_passed": self.monitors_passed,
            "monitors_failed": self.monitors_failed,
        }
        context.update(self.context)
        return context
