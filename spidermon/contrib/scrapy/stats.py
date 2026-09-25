from __future__ import annotations

from typing import TYPE_CHECKING

from slugify import slugify

if TYPE_CHECKING:
    from scrapy.statscollectors import StatsCollector

STATS_DEFAULT_VALIDATION_PREFIX = "spidermon/validation"


class NAMES:
    ITEMS = "items"
    DROPPED = "dropped"
    FIELDS = "fields"
    ERRORS = "errors"
    VALIDATORS = "validators"


class ValidationStatsManager:
    def __init__(
        self, stats: StatsCollector, prefix: str | None = None, slugify: bool = True
    ) -> None:
        self.stats = stats
        self.prefix = prefix or STATS_DEFAULT_VALIDATION_PREFIX
        self.slugify = slugify

    def add_validator(self, type: str, class_name: str) -> None:  # noqa: A002
        self.stats.inc_value(self._get_stats_name(NAMES.VALIDATORS))
        self.stats.set_value(
            self._get_stats_name(NAMES.VALIDATORS, type, class_name),
            True,
        )

    def add_field_error(self, field: str, error: str) -> None:
        self.stats.inc_value(self._get_stats_name(NAMES.FIELDS, NAMES.ERRORS))
        self.stats.inc_value(self._get_stats_name(NAMES.FIELDS, NAMES.ERRORS, error))
        self.stats.inc_value(
            self._get_stats_name(NAMES.FIELDS, NAMES.ERRORS, error) + "/" + field,
        )

    def add_fields(self, count: int) -> None:
        self.stats.inc_value(self._get_stats_name(NAMES.FIELDS), count=count)

    def add_item(self) -> None:
        self.stats.inc_value(self._get_stats_name(NAMES.ITEMS))

    def add_dropped_item(self) -> None:
        self.stats.inc_value(self._get_stats_name(NAMES.ITEMS, NAMES.DROPPED))

    def add_item_with_errors(self) -> None:
        self.stats.inc_value(self._get_stats_name(NAMES.ITEMS, NAMES.ERRORS))

    def _get_stats_name(self, *names: str) -> str:
        return "/".join([self.prefix, *map(self._get_name, names)])

    def _get_name(self, name: str) -> str:
        return slugify(text=name, separator="_").lower() if self.slugify else name
