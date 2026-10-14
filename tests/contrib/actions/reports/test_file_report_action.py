from pathlib import Path

import pytest
from pytest_mock import MockerFixture

pytest.importorskip("jinja2")

from spidermon.contrib.actions.reports.files import CreateFileReport


def test_after_render_report_writes_utf8(tmp_path: Path, mocker: MockerFixture) -> None:
    target = tmp_path / "report.html"
    report = CreateFileReport(template="report.jinja", filename=str(target))
    report.report = "报告"
    report.result = mocker.MagicMock()
    report.after_render_report()

    assert target.read_text(encoding="utf-8") == "报告"
