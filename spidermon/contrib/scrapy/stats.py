from __future__ import absolute_import
from slugify import slugify


STATS_DEFAULT_VALIDATION_PREFIX = "spidermon/validation"


class NAMES:
    ITEMS = "items"
    DROPPED = "dropped"
    FIELDS = "fields"
    ERRORS = "errors"
    VALIDATORS = "validators"


class ValidationStatsManager(object):
    def __init__(self, stats, prefix=None, slugify=True):
        self.stats = stats
        self.prefix = prefix or STATS_DEFAULT_VALIDATION_PREFIX
        self.slugify = slugify

    def add_validator(self, type, class_name):
        self.stats.inc_value(self._get_stats_name(NAMES.VALIDATORS))
        self.stats.set_value(
            self._get_stats_name(NAMES.VALIDATORS, type, class_name), True
        )

    def add_field_error(self, field, error):
        self.stats.inc_value(self._get_stats_name(NAMES.FIELDS, NAMES.ERRORS))
        self.stats.inc_value(self._get_stats_name(NAMES.FIELDS, NAMES.ERRORS, error))
        self.stats.inc_value(
            self._get_stats_name(NAMES.FIELDS, NAMES.ERRORS, error) + "/" + field
        )

    def add_fields(self, count):
        self.stats.inc_value(self._get_stats_name(NAMES.FIELDS), count=count)

    def add_item(self):
        self.stats.inc_value(self._get_stats_name(NAMES.ITEMS))

    def add_dropped_item(self):
        self.stats.inc_value(self._get_stats_name(NAMES.ITEMS, NAMES.DROPPED))

    def add_item_with_errors(self):
        self.stats.inc_value(self._get_stats_name(NAMES.ITEMS, NAMES.ERRORS))

    def _get_stats_name(self, *names):
        return "/".join([self.prefix] + list([self._get_name(n) for n in names]))

    def _get_name(self, name):
        return slugify(text=name, separator="_").lower() if self.slugify else name
