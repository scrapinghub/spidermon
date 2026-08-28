import datetime

import pytest

pytest.importorskip("jinja2")

from spidermon.contrib.actions.reports import CreateReport
from spidermon.data import Data


def _report(stats):
    report = CreateReport(template="reports/email/monitors/result.jinja")
    report.result = Data(
        {
            "monitor_results": [],
            "monitors_passed_results": [],
            "monitors_failed_results": [],
            "all_monitors_passed": True,
        },
    )
    report.data = Data(
        {
            "spider": Data({"name": "myspider"}),
            "sc_spider_name": "myspider",
            "stats": stats,
        },
    )
    report.render_report()
    return report.report


# The report footer also calls the deprecated datetime.datetime.utcnow(),
# unrelated to the running-time calculation under test here.
pytestmark = pytest.mark.filterwarnings(
    "ignore:datetime.datetime.utcnow\\(\\) is deprecated:DeprecationWarning",
)


def test_render_report_while_spider_is_still_running():
    # `finish_time` is only present in stats once the spider closes, e.g.
    # a periodic monitor can run while the spider is still going. Scrapy
    # stores these timestamps as naive UTC datetimes.
    stats = {"start_time": datetime.datetime(2024, 1, 1, 12, 0, 0)}  # noqa: DTZ001
    report = _report(stats)
    assert "myspider" in report


def test_render_report_after_spider_finished():
    stats = {
        "start_time": datetime.datetime(2024, 1, 1, 12, 0, 0),  # noqa: DTZ001
        "finish_time": datetime.datetime(2024, 1, 1, 12, 5, 0),  # noqa: DTZ001
    }
    report = _report(stats)
    assert "myspider" in report
