from __future__ import absolute_import
import os
import inspect

from spidermon.core.actions import ActionOptionsMetaclass, Action
from spidermon.templates import template_loader, Template
import six


class ActionWithTemplatesMetaclass(ActionOptionsMetaclass):
    def __new__(mcs, name, bases, attrs):
        cls = super(ActionWithTemplatesMetaclass, mcs).__new__(mcs, name, bases, attrs)
        mcs.add_class_templates(cls)
        return cls

    @classmethod
    def add_class_templates(mcs, cls):
        class_file = inspect.getfile(cls)
        class_path = os.path.dirname(class_file)
        template_loader.discover_folder(class_path)
        for path in cls.template_paths:
            template_path = os.path.join(class_path, path)
            template_loader.add_path(template_path)


class ActionWithTemplates(six.with_metaclass(ActionWithTemplatesMetaclass, Action)):
    template_paths = []
    context = None

    def __init__(self, context=None):
        super(ActionWithTemplates, self).__init__()
        self.context = context or self.context or {}

    def get_template(self, name):
        return template_loader.get_template(name)

    def render_text_template(self, template):
        template = Template(template)
        return template.render(self.get_template_context())

    def render_template(self, template):
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
