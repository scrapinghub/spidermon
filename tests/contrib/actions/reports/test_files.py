import pytest

from spidermon.contrib.actions.reports.files import CreateFileReport
from spidermon.exceptions import NotConfigured

TEMPLATE = "template"
FILENAME = "filename"


def test_init_without_params():
    with pytest.raises(TypeError):
        CreateFileReport()


def test_init_with_template_param_only():
    with pytest.raises(TypeError):
        CreateFileReport(template=TEMPLATE)


def test_init_with_invalid_params():
    with pytest.raises(NotConfigured) as e:
        CreateFileReport(template=TEMPLATE, filename=None)
    assert "You must define a template output file." in str(e.value)


def test_init_with_valid_params():
    report = CreateFileReport(template=TEMPLATE, filename=FILENAME)
    assert report.filename == FILENAME


def test_after_render_report(mocker):
    _open = mocker.patch("spidermon.contrib.actions.reports.files.open", new_callable=mocker.mock_open())
    report = CreateFileReport(template=TEMPLATE, filename=FILENAME)
    report.render_template = mocker.MagicMock(return_value="render_template")
    report.render_text_template = mocker.MagicMock(return_value="rendered_filename")
    report.report = "report data"
    report.after_render_report()
    report.render_text_template.assert_called_once_with(FILENAME)
    _open.assert_called_once_with("rendered_filename", "w")
    # Write is inside a context manager, so we need to call __enter__()
    _open().__enter__().write.assert_called_once_with("report data")
