from pathlib import Path

import pytest

pytest.importorskip("jinja2")

import jinja2

from spidermon.templates import TemplateLoader


def create_file(path, content):
    Path(path).write_text(content)


def test_get_template_with_absolute_path(tmpdir):
    template_loader = TemplateLoader()
    test_template = Path(tmpdir) / "absolute_path_template.jinja"
    create_file(test_template, "test content")

    assert str(tmpdir) not in template_loader.paths
    template = template_loader.get_template(test_template)
    assert template.render() == "test content"


def test_fail_get_absolute_template_that_does_not_exist(tmpdir):
    template_loader = TemplateLoader()
    test_template = Path(tmpdir) / "i_do_not_exist.template"
    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        template_loader.get_template(test_template)


def test_fail_get_template_that_does_not_exist(tmpdir):
    template_loader = TemplateLoader()
    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        template_loader.get_template("i_do_not_exist.template")
