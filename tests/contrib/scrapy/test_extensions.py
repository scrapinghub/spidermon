from functools import partial
from unittest import TestCase

import pytest

pytest.importorskip("scrapy")


from scrapy import Spider
from scrapy.utils.test import get_crawler

from spidermon.contrib.scrapy import extensions as ext_module
from spidermon.contrib.scrapy.extensions import Spidermon
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner


class TestSpiderMonitorRunner(SpiderMonitorRunner):
    __test__ = False

    def run_monitors(self):
        self.result.next_step()
        res = self.suite.run(self.result)
        raise AssertionError((res.failures, res.errors))


def _test_run_suites(self, spider, suites):
    data = self._generate_data_for_spider(spider)
    for suite in suites:
        runner = TestSpiderMonitorRunner(spider=spider)
        runner.run(suite, **data)


class TestData:
    __test__ = False

    def __init__(self, expression, stats=None, settings=None, expected_error=None):
        if stats is None:
            stats = {}
        if settings is None:
            settings = {}

        self.stats = stats
        self.expression = expression
        self.settings = settings
        self.expected_error = expected_error


class ExpressionMonitorsTesting(TestCase):
    """
    Tests if expression monitors, which defined in settings, properly configured:
        - SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS,
        - SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS,

    Test case only for expression monitors firing at the spider's opening, but at
    closing time logic are the same, as well as way of loading test suites.

    Makes sure that all context components are available for usage, these are
    supposed to be configured and existed in the context of expressions:
        - stats,
        - crawler,
        - spider,
        - job,
        - validation,
        - responses

    NotConfigured error should also fire only in appropriate time: when interpreter
    evaluates expressions.
    """

    spider_name = "test"

    def run_test(self, **kwargs):
        dt = TestData(**kwargs)
        settings = {
            "SPIDERMON_ENABLED": True,
            "SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS": [
                {"tests": [{"expression": dt.expression}]},
            ],
        }
        settings.update(dt.settings)
        crawler = get_crawler(settings_dict=settings)
        crawler.stats.get_stats = lambda: dt.stats
        spidermon = Spidermon.from_crawler(crawler)
        spider = Spider(name=self.spider_name)

        # mocking, to see test results via raising AssertionError exception
        # with failures and errors as results
        spidermon._run_suites = partial(_test_run_suites, spidermon)

        try:
            spidermon.spider_opened(spider)
        except AssertionError as ae:
            failures, errors = ae.args[0]
            for f in failures:
                _, trace = f
                raise AssertionError(trace) from ae
            for err in errors:
                _, trace = err
                if dt.expected_error and dt.expected_error in trace:
                    dt.expected_error = None
                else:
                    raise AssertionError(trace) from ae
            if dt.expected_error:
                raise AssertionError(
                    f"Expected error <{dt.expected_error}> was not raised",
                ) from ae

    def test_stats_ready(self):
        self.run_test(
            stats={"finish_reason": "dead"},
            expression="stats.finish_reason == 'dead'",
        )

    def test_stats_not_configured(self):
        self.run_test(
            expression="stats.finish_reason == 'dead'",
            expected_error="NotConfigured",
        )

    def test_crawler_ready(self):
        self.run_test(
            settings={"special_check": "12345"},
            expression="crawler.settings['special_check'] == '12345'",
        )

    def test_spider_ready(self):
        self.run_test(expression=f"spider.name == '{self.spider_name}'")

    def test_responses_ready(self):
        self.run_test(
            stats={"finish_reason": "dead"},  # any stats, responses created from stats
            expression="responses.count == 0",
        )

    def test_responses_not_configured(self):
        self.run_test(expression="responses.count == 0", expected_error="NotConfigured")

    def test_validation_ready(self):
        self.run_test(
            stats={"finish_reason": "dead"},  # any stats, validation created from stats
            expression="validation.items.count == 0",
        )

    def test_validation_not_configured(self):
        self.run_test(
            expression="validation.items.count == 0",
            expected_error="NotConfigured",
        )

    def test_job_not_configured(self):
        # job is not configured, but existed in the context
        self.run_test(
            expression="job.metadata['finish_reason' == 'dead']",
            expected_error="NotConfigured",
        )

    def test_inappropriate_context(self):
        # expected something like <NameError: name 'foo' is not defined>
        self.run_test(expression="foo.bar == 'boo'", expected_error="NameError")


def test_skip_values_helpers_cover_all_normalization_paths():
    ext = Spidermon.__new__(Spidermon)
    assert ext._get_skip_values_list(
        get_crawler(settings_dict={"SPIDERMON_ENABLED": True}).settings
    ) == ["", [], {}, "N/A", "-"]
    assert ext._get_skip_values_list(
        get_crawler(
            settings_dict={
                "SPIDERMON_ENABLED": True,
                "SPIDERMON_FIELD_COVERAGE_SKIP_VALUES": [],
            }
        ).settings
    ) == []
    assert ext._get_skip_values_list(
        get_crawler(
            settings_dict={
                "SPIDERMON_ENABLED": True,
                "SPIDERMON_FIELD_COVERAGE_SKIP_VALUES": [0, "N/A"],
            }
        ).settings
    ) == [0, "N/A"]
    assert ext._get_skip_values_list(
        get_crawler(
            settings_dict={
                "SPIDERMON_ENABLED": True,
                "SPIDERMON_FIELD_COVERAGE_SKIP_VALUES": '[0, -1, "N/A"]',
            }
        ).settings
    ) == [0, -1, "N/A"]
    assert ext._get_skip_values_list(
        get_crawler(
            settings_dict={
                "SPIDERMON_ENABLED": True,
                "SPIDERMON_FIELD_COVERAGE_SKIP_VALUES": "42",
            }
        ).settings
    ) == ["42"]
    assert ext._get_skip_values_list(
        get_crawler(
            settings_dict={
                "SPIDERMON_ENABLED": True,
                "SPIDERMON_FIELD_COVERAGE_SKIP_VALUES": "TBD,unknown",
            }
        ).settings
    ) == ["TBD", "unknown"]
    assert ext._get_skip_values_list(
        get_crawler(
            settings_dict={
                "SPIDERMON_ENABLED": True,
                "SPIDERMON_FIELD_COVERAGE_SKIP_VALUES": (0, -1),
            }
        ).settings
    ) == [0, -1]


def test_value_match_is_type_sensitive():
    ext = Spidermon.__new__(Spidermon)
    assert ext._value_matches_skip_entry(0, 0)
    assert not ext._value_matches_skip_entry(False, 0)
    assert not ext._value_matches_skip_entry("0", 0)
    assert ext._value_in_skip_values("N/A", ["N/A"])
    assert not ext._value_in_skip_values("N/A", [0, 1, "-"])


def test_load_suite_error_paths(monkeypatch):
    ext = Spidermon.__new__(Spidermon)
    ext.crawler = get_crawler(settings_dict={"SPIDERMON_ENABLED": True})

    def raiser(_suite):
        raise RuntimeError("boom")

    monkeypatch.setattr(ext_module, "load_object", raiser)
    with pytest.raises(RuntimeError, match="boom"):
        ext.load_suite("x.y.Suite")

    monkeypatch.setattr(ext_module, "load_object", lambda _suite: dict)
    with pytest.raises(Exception):
        ext.load_suite("x.y.NotAMonitorSuite")


def test_load_expression_suite_with_custom_monitor_class(monkeypatch):
    ext = Spidermon.__new__(Spidermon)
    ext.crawler = get_crawler(settings_dict={"SPIDERMON_ENABLED": True})

    from spidermon.python.monitors import ExpressionsMonitor

    monkeypatch.setattr(ext_module, "load_object", lambda _path: ExpressionsMonitor)

    from spidermon.python import factory

    monkeypatch.setattr(
        factory,
        "create_monitor_class_from_dict",
        lambda monitor_dict, monitor_class: monitor_class,
    )

    suite = ext.load_expression_suite(
        {"tests": [{"expression": "True"}]},
        monitor_class="spidermon.python.monitors.ExpressionsMonitor",
    )
    assert suite is not None


def test_count_item_skip_branches():
    crawler = get_crawler(settings_dict={"SPIDERMON_ENABLED": True})
    ext = Spidermon.from_crawler(crawler)

    # skip_values None path + falsy skipping branch
    ext._count_item(
        {"empty": "", "zero": 0, "ok": "value"},
        skip_none_values=False,
        skip_falsy_values=True,
        skip_values=None,
    )
    stats = crawler.stats.get_stats()
    assert stats.get("spidermon_item_scraped_count/dict/ok") == 1
    assert stats.get("spidermon_item_scraped_count/dict/empty") is None
    assert stats.get("spidermon_item_scraped_count/dict/zero") is None

    # explicit skip_values branch
    ext._count_item(
        {"placeholder": "N/A", "ok2": "value"},
        skip_none_values=False,
        skip_falsy_values=False,
        skip_values=["N/A"],
    )
    stats = crawler.stats.get_stats()
    assert stats.get("spidermon_item_scraped_count/dict/placeholder") is None
    assert stats.get("spidermon_item_scraped_count/dict/ok2") == 1


def test_periodic_monitor_paths(monkeypatch):
    ext = Spidermon.__new__(Spidermon)
    ext.periodic_suites = {"a.suite": 10}
    ext.periodic_tasks = {}
    ext.spider_opened_suites = []
    ext.spider_closed_suites = []
    ext._run_suites = lambda spider, suites: None
    ext._add_field_coverage_to_stats = lambda: None

    class DummyLoopingCall:
        def __init__(self, _func, *_args):
            self.started = False
            self.stopped = False

        def start(self, _time, now=False):
            self.started = True
            self.now = now

        def stop(self):
            self.stopped = True

    monkeypatch.setattr(ext_module, "LoopingCall", DummyLoopingCall)

    spider = Spider(name="periodic")
    ext.spider_opened(spider)
    assert ext.periodic_tasks[spider][0].started is True

    ext.spider_closed(spider)
    assert ext.periodic_tasks[spider][0].stopped is True

    captured = {}
    ext.load_suite = lambda s: f"loaded:{s}"
    ext._run_suites = lambda spider, suites: captured.setdefault("suites", suites)
    ext._run_periodic_suites(spider, ["x.suite"])
    assert captured["suites"] == ["loaded:x.suite"]


def test_item_scraped_reads_skip_settings():
    settings = {
        "SPIDERMON_ENABLED": True,
        "SPIDERMON_ADD_FIELD_COVERAGE": True,
        "SPIDERMON_FIELD_COVERAGE_SKIP_FALSY": True,
    }
    crawler = get_crawler(settings_dict=settings)
    spider = Spider.from_crawler(crawler, "example.com")
    ext = Spidermon.from_crawler(crawler)

    observed = {}

    def fake_count_item(*args, **kwargs):
        observed["args"] = args
        observed["kwargs"] = kwargs

    ext._count_item = fake_count_item
    ext.item_scraped({"field1": "value1"}, None, spider)

    # args: item, skip_none_values, skip_falsy_values, skip_values
    assert observed["args"][2] is True
    assert observed["args"][3] == ["", [], {}, "N/A", "-"]
