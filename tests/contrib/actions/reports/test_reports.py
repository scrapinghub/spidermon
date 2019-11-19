try:
    from unittest.mock import MagicMock, patch, call, mock_open
except ImportError:
    from mock import MagicMock, patch, call, mock_open
import pytest
from unittest import TestCase

from spidermon.contrib.actions.reports import CreateReport
from spidermon.exceptions import NotConfigured

TEMPLATE = "template"
FILENAME = "filename"


class CreateReportTests(TestCase):
    def test_init_with_invalid_params(self):
        with pytest.raises(NotConfigured) as e:
            CreateReport()
        assert "You must define one template file." in str(e.value)

    def test_init_with_valid_params(self):
        report = CreateReport(template=TEMPLATE)
        assert report.template == TEMPLATE

    def test_run_action(self):
        report = CreateReport(template=TEMPLATE)
        report.before_render_report = MagicMock()
        report.render_report = MagicMock()
        report.after_render_report = MagicMock()
        report.run_action()

        report.before_render_report.assert_called_once_with()
        report.render_report.assert_called_once_with()
        report.after_render_report.assert_called_once_with()

    def test_render_report(self):
        report = CreateReport(template=TEMPLATE)
        report.render_template = MagicMock()
        report.render_report()
        report.render_template.assert_called_once_with(TEMPLATE)
