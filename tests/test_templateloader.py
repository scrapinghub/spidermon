import os

from spidermon.templates import TemplateLoader


def create_file(path, content):
    with open(path, "w") as file:
        file.write(content)


def test_get_template_with_absolute_path_updates_templateloader_paths(tmpdir):
    template_loader = TemplateLoader()
    test_template = os.path.join(str(tmpdir), "absolute_path_template.jinja")
    create_file(test_template, "test content")

    assert tmpdir not in template_loader.paths
    template = template_loader.get_template(test_template)
    assert template.render() == "test content"
