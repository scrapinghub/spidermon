try:
    from unittest.mock import MagicMock, patch, mock_open
except ImportError:
    from mock import MagicMock, patch, mock_open
import pytest
from unittest import TestCase

from spidermon.contrib.actions.reports.files import CreateFileReport
from spidermon.exceptions import NotConfigured

TEMPLATE = "template"
FILENAME = "filename"


class CreateFileReportTests(TestCase):
    def test_init_without_params(self):
        with pytest.raises(TypeError):
            CreateFileReport()

    def test_init_with_template_param_only(self):
        with pytest.raises(TypeError):
            CreateFileReport(template=TEMPLATE)

    def test_init_with_invalid_params(self):
        with pytest.raises(NotConfigured) as e:
            CreateFileReport(template=TEMPLATE, filename=None)
        assert "You must define a template output file." in str(e.value)

    def test_init_with_valid_params(self):
        report = CreateFileReport(template=TEMPLATE, filename=FILENAME)
        assert report.filename == FILENAME

    @patch("spidermon.contrib.actions.reports.files.open", new_callable=mock_open())
    def test_after_render_report(self, _open):
        report = CreateFileReport(template=TEMPLATE, filename=FILENAME)
        report.render_template = MagicMock(return_value="render_template")
        report.render_text_template = MagicMock(return_value="rendered_filename")
        report.report = "report data"
        report.after_render_report()
        report.render_text_template.assert_called_once_with(FILENAME)
        _open.assert_called_once_with("rendered_filename", "w")
        # Write is inside a context manager, so we need to call __enter__()
        _open().__enter__().write.assert_called_once_with("report data")
