import pytest
from unittest import TestCase

from spidermon.contrib.actions.reports import CreateReport
from spidermon.exceptions import NotConfigured

TEMPLATE = "template"
FILENAME = "filename"


def test_init_with_invalid_params():
    with pytest.raises(NotConfigured) as e:
        CreateReport()
    assert "You must define one template file." in str(e.value)


def test_init_with_valid_params():
    report = CreateReport(template=TEMPLATE)
    assert report.template == TEMPLATE


def test_run_action(mocker):
    report = CreateReport(template=TEMPLATE)
    report.before_render_report = mocker.MagicMock()
    report.render_report = mocker.MagicMock()
    report.after_render_report = mocker.MagicMock()
    report.run_action()

    report.before_render_report.assert_called_once_with()
    report.render_report.assert_called_once_with()
    report.after_render_report.assert_called_once_with()


def test_render_report(mocker):
    report = CreateReport(template=TEMPLATE)
    report.render_template = mocker.MagicMock()
    report.render_report()
    report.render_template.assert_called_once_with(TEMPLATE)
