from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from itemadapter import ItemAdapter
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.utils.misc import load_object
from twisted.internet.task import LoopingCall

from spidermon import MonitorSuite
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner
from spidermon.contrib.utils.spider import get_spider_name
from spidermon.python.monitors import ExpressionsMonitor
from spidermon.utils.field_coverage import calculate_field_coverage
from spidermon.utils.zyte import Client

if TYPE_CHECKING:
    from collections.abc import Iterable

    from scrapy import Spider
    from scrapy.crawler import Crawler
    from scrapy.http import Response
    from scrapy.settings import BaseSettings


class Spidermon:
    def __init__(  # noqa: PLR0913, PLR0917
        self,
        crawler: Crawler,
        spider_opened_suites: list[str | type[MonitorSuite]] | None = None,
        spider_closed_suites: list[str | type[MonitorSuite]] | None = None,
        engine_stopped_suites: list[str | type[MonitorSuite]] | None = None,
        spider_opened_expression_suites: list[dict[str, Any]] | None = None,
        spider_closed_expression_suites: list[dict[str, Any]] | None = None,
        engine_stopped_expression_suites: list[dict[str, Any]] | None = None,
        expressions_monitor_class: str | type[ExpressionsMonitor] | None = None,
        periodic_suites: dict[str | type[MonitorSuite], float] | None = None,
    ) -> None:
        if not crawler.settings.getbool("SPIDERMON_ENABLED"):
            raise NotConfigured
        self.crawler = crawler

        self.spider_opened_suites = [
            self.load_suite(s) for s in spider_opened_suites or []
        ]
        self.spider_opened_suites += [
            self.load_expression_suite(s, expressions_monitor_class)
            for s in spider_opened_expression_suites or []
        ]

        self.spider_closed_suites = [
            self.load_suite(s) for s in spider_closed_suites or []
        ]
        self.spider_closed_suites += [
            self.load_expression_suite(s, expressions_monitor_class)
            for s in spider_closed_expression_suites or []
        ]

        self.engine_stopped_suites = [
            self.load_suite(s) for s in engine_stopped_suites or []
        ]
        self.engine_stopped_suites += [
            self.load_expression_suite(s, expressions_monitor_class)
            for s in engine_stopped_expression_suites or []
        ]

        self.periodic_suites = periodic_suites or {}
        self.periodic_tasks: dict[Spider, list[LoopingCall]] = {}
        self.client = Client(self.crawler.settings)

    @staticmethod
    def _get_default_skip_values() -> list[Any]:
        """Default ``SPIDERMON_FIELD_COVERAGE_SKIP_VALUES`` when the setting is unset.

        Includes values that are also Python-falsy (``""``, ``[]``, ``{}``) and
        truthy placeholders (``"N/A"``, ``"-"``) that must be matched explicitly.
        Falsy skipping is controlled separately by ``SPIDERMON_FIELD_COVERAGE_SKIP_FALSY``.
        """
        return ["", [], {}, "N/A", "-"]

    @staticmethod
    def _value_matches_skip_entry(value: Any, candidate: Any) -> bool:
        """Exact match for skip list: same type and equal value.

        Plain ``==`` / ``in`` would conflate ``bool`` with ``int`` (``False == 0``).
        """
        return type(value) is type(candidate) and value == candidate

    def _value_in_skip_values(self, value: Any, skip_values: Iterable[Any]) -> bool:
        return any(self._value_matches_skip_entry(value, s) for s in skip_values)

    def _get_skip_values_list(self, settings: BaseSettings) -> list[Any]:
        """Get skip values list, supporting Python lists, JSON strings, and
        comma-separated strings.

        This allows preserving types (e.g., integers) when provided as Python
        lists or JSON strings, while still supporting comma-separated strings
        for backward compatibility.

        Default skip values: empty string, empty list, empty dict, 'N/A', '-'
        """
        # Default skip values
        default_skip_values = self._get_default_skip_values()

        value = settings.get("SPIDERMON_FIELD_COVERAGE_SKIP_VALUES", None)
        if value is None:
            return default_skip_values

        if not value:
            return []

        # If it's already a list, return it (preserves types)
        if isinstance(value, list):
            return value

        # If it's a string, try to parse as JSON first (preserves types)
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                # If JSON parsing succeeds and returns a list, use it
                if isinstance(parsed, list):
                    return parsed
            except (ValueError, TypeError):
                # If JSON parsing fails, fall back to comma-separated string
                pass

            # Fall back to Scrapy's getlist (converts to list of strings)
            return settings.getlist("SPIDERMON_FIELD_COVERAGE_SKIP_VALUES", [])

        # For any other type, try to convert to list
        return list(value) if value else []

    def load_suite(self, suite_to_load: str | type[MonitorSuite]) -> MonitorSuite:
        suite_class = load_object(suite_to_load)
        if not issubclass(suite_class, MonitorSuite):
            raise TypeError(f"{suite_to_load} is not a MonitorSuite subclass")
        suite: MonitorSuite = suite_class(crawler=self.crawler)
        return suite

    def load_expression_suite(
        self,
        suite_to_load: dict[str, Any],
        monitor_class: str | type[ExpressionsMonitor] | None = None,
    ) -> MonitorSuite:
        monitor_cls: type[ExpressionsMonitor] = (
            load_object(monitor_class) if monitor_class else ExpressionsMonitor
        )

        from spidermon.python import factory  # noqa: PLC0415

        monitor = factory.create_monitor_class_from_dict(
            monitor_dict=suite_to_load,
            monitor_class=monitor_cls,
        )
        suite = MonitorSuite(crawler=self.crawler)
        suite.add_monitor(monitor)
        return suite

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Spidermon:
        ext = cls(
            crawler=crawler,
            spider_opened_suites=crawler.settings.getlist(
                "SPIDERMON_SPIDER_OPEN_MONITORS",
            ),
            spider_closed_suites=crawler.settings.getlist(
                "SPIDERMON_SPIDER_CLOSE_MONITORS",
            ),
            engine_stopped_suites=crawler.settings.getlist(
                "SPIDERMON_ENGINE_STOP_MONITORS",
            ),
            spider_opened_expression_suites=crawler.settings.getlist(
                "SPIDERMON_SPIDER_OPEN_EXPRESSION_MONITORS",
            ),
            spider_closed_expression_suites=crawler.settings.getlist(
                "SPIDERMON_SPIDER_CLOSE_EXPRESSION_MONITORS",
            ),
            engine_stopped_expression_suites=crawler.settings.getlist(
                "SPIDERMON_ENGINE_STOP_EXPRESSION_MONITORS",
            ),
            expressions_monitor_class=crawler.settings.get(
                "SPIDERMON_EXPRESSIONS_MONITOR_CLASS",
            ),
            periodic_suites=crawler.settings.getdict("SPIDERMON_PERIODIC_MONITORS"),
        )
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.engine_stopped, signal=signals.engine_stopped)

        has_field_coverage = crawler.settings.getbool("SPIDERMON_ADD_FIELD_COVERAGE")

        if has_field_coverage:
            crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)

        return ext

    def spider_opened(self, spider: Spider) -> None:
        self._run_suites(spider, self.spider_opened_suites)
        self.periodic_tasks[spider] = []
        for suite, time in self.periodic_suites.items():
            task = LoopingCall(self._run_periodic_suites, spider, [suite])
            self.periodic_tasks[spider].append(task)
            task.start(time, now=False)

    def spider_closed(self, spider: Spider) -> None:
        self._add_field_coverage_to_stats()

        self._run_suites(spider, self.spider_closed_suites)
        for task in self.periodic_tasks[spider]:
            if task.running:
                task.stop()

    def engine_stopped(self) -> None:
        spider = self.crawler.spider
        assert spider is not None
        self._run_suites(spider, self.engine_stopped_suites)

    def _count_item(  # noqa: PLR0913,PLR0912,PLR0917
        self,
        item: Any,
        skip_none_values: bool,
        skip_falsy_values: bool,
        skip_values: list[Any] | None = None,
        item_count_stat: str | None = None,
        max_list_nesting_level: int = 0,
        max_dict_nesting_level: int = -1,
        nesting_level: int = 0,
        per_field_dict_levels: dict[str, Any] | None = None,
    ) -> None:
        if item_count_stat is None:
            item_type = type(item).__name__
            item_count_stat = f"spidermon_item_scraped_count/{item_type}"
            self.crawler.stats.inc_value(item_count_stat)

        if skip_values is None:
            skip_values = []

        for field_name, value in ItemAdapter(item).items():
            if skip_none_values and value is None:
                continue

            if skip_falsy_values and value is not None and not value:
                continue

            if self._value_in_skip_values(value, skip_values):
                continue

            field_item_count_stat = f"{item_count_stat}/{field_name}"
            self.crawler.stats.inc_value(field_item_count_stat)

            # Resolve per-field level at the top nesting level only
            if per_field_dict_levels is not None and nesting_level == 0:
                effective_max_dict = int(
                    per_field_dict_levels.get(
                        field_name,
                        per_field_dict_levels.get("*", -1),
                    )
                )
            else:
                effective_max_dict = max_dict_nesting_level

            if isinstance(value, dict):
                # if there's no max (set to -1), we just proceed indefinitely (all levels)
                # this is for backwards compatibility
                if effective_max_dict == -1:
                    self._count_item(
                        value,
                        skip_none_values,
                        skip_falsy_values,
                        skip_values,
                        field_item_count_stat,
                        max_list_nesting_level=max_list_nesting_level,
                        max_dict_nesting_level=effective_max_dict,
                        nesting_level=nesting_level + 1,
                    )
                    continue
                if effective_max_dict > -1 and nesting_level < effective_max_dict:
                    self._count_item(
                        value,
                        skip_none_values,
                        skip_falsy_values,
                        skip_values,
                        field_item_count_stat,
                        nesting_level=nesting_level + 1,
                        max_list_nesting_level=max_list_nesting_level,
                        max_dict_nesting_level=effective_max_dict,
                    )
                    continue

                continue

            if (
                isinstance(value, list)
                and max_list_nesting_level > 0
                and nesting_level < max_list_nesting_level
            ):
                items_count_stat = f"{field_item_count_stat}/_items"
                for list_item in value:
                    self.crawler.stats.inc_value(items_count_stat)
                    if isinstance(list_item, dict):
                        self._count_item(
                            list_item,
                            skip_none_values,
                            skip_falsy_values,
                            skip_values,
                            items_count_stat,
                            max_list_nesting_level=max_list_nesting_level,
                            max_dict_nesting_level=effective_max_dict,
                            nesting_level=nesting_level + 1,
                        )
                        continue

    def _add_field_coverage_to_stats(self) -> None:
        stats = self.crawler.stats.get_stats()
        coverage_stats = calculate_field_coverage(stats)
        stats.update(coverage_stats)

    def item_scraped(
        self, item: Any, response: Response | None, spider: Spider
    ) -> None:
        skip_none_values = spider.crawler.settings.getbool(
            "SPIDERMON_FIELD_COVERAGE_SKIP_NONE",
            False,
        )
        skip_falsy_values = spider.crawler.settings.getbool(
            "SPIDERMON_FIELD_COVERAGE_SKIP_FALSY", True
        )
        skip_values = self._get_skip_values_list(spider.crawler.settings)

        list_field_coverage_levels = spider.crawler.settings.getint(
            "SPIDERMON_LIST_FIELDS_COVERAGE_LEVELS",
            0,
        )
        dict_field_coverage_setting = spider.crawler.settings.get(
            "SPIDERMON_DICT_FIELDS_COVERAGE_LEVELS",
            -1,
        )
        if isinstance(dict_field_coverage_setting, dict):
            per_field_dict_levels = dict_field_coverage_setting
            dict_field_coverage_levels = -1
        else:
            per_field_dict_levels = None
            dict_field_coverage_levels = int(dict_field_coverage_setting)
        self.crawler.stats.inc_value("spidermon_item_scraped_count")
        self._count_item(
            item,
            skip_none_values,
            skip_falsy_values,
            skip_values,
            max_list_nesting_level=list_field_coverage_levels,
            max_dict_nesting_level=dict_field_coverage_levels,
            per_field_dict_levels=per_field_dict_levels,
        )

    def _run_periodic_suites(
        self, spider: Spider, suites: list[str | type[MonitorSuite]]
    ) -> None:
        self._run_suites(spider, [self.load_suite(s) for s in suites])

    def _run_suites(self, spider: Spider, suites: list[MonitorSuite]) -> None:
        data = self._generate_data_for_spider(spider)
        for suite in suites:
            runner = SpiderMonitorRunner(spider=spider)
            runner.run(suite, **data)

    def _generate_data_for_spider(self, spider: Spider) -> dict[str, Any]:
        return {
            "stats": self.crawler.stats.get_stats(),
            "stats_history": (
                spider.stats_history if hasattr(spider, "stats_history") else []
            ),
            "crawler": self.crawler,
            "spider": spider,
            "sc_spider_name": get_spider_name(spider),
            "job": self.client.job if self.client.available else None,
        }
