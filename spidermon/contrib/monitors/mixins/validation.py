from __future__ import absolute_import
from spidermon.contrib.stats.counters import (
    PercentCounter,
    DictPercentCounter,
    AttributeDictPercentCounter,
)
from spidermon.contrib.stats.analyzer import StatsAnalyzer
from spidermon.contrib.scrapy.stats import STATS_DEFAULT_VALIDATION_PREFIX

from .stats import StatsMonitorMixin


class MetaDictPercentCounter(DictPercentCounter):
    def add_values(self, key, subkey, value):
        if key not in self._dict:
            self._create_item(key)
        self[key].add_value(subkey, value)


class ErrorsDictPercentCounter(AttributeDictPercentCounter):
    __attribute_dict_name__ = "fields"


class ErrorsInfo(MetaDictPercentCounter):
    __items_class__ = ErrorsDictPercentCounter


class FieldErrorsDictPercentCounter(AttributeDictPercentCounter):
    __attribute_dict_name__ = "errors"


class FieldErrorsInfo(MetaDictPercentCounter):
    __items_class__ = FieldErrorsDictPercentCounter

    def __init__(self, fields_count, items_count):
        super(FieldErrorsInfo, self).__init__(items_count)
        self._fields_count = fields_count

    @property
    def count(self):
        return self._fields_count


class ItemsInfo(object):
    def __init__(self, items_count, items_with_errors, items_dropped):
        self.count = items_count
        self.errors = PercentCounter(count=items_with_errors, total=items_count)
        self.dropped = PercentCounter(count=items_dropped, total=items_count)


class ValidationInfo(object):
    def __init__(self, stats, prefix=None):
        self.analyzer = StatsAnalyzer(
            stats=stats, prefix=prefix or STATS_DEFAULT_VALIDATION_PREFIX
        )

        # items
        items_count = sum(self.analyzer.search("items$").values())
        items_with_errors_count = sum(self.analyzer.search("items/errors$").values())
        items_dropped_count = sum(self.analyzer.search("items/dropped$").values())
        self.items = ItemsInfo(
            items_count=items_count,
            items_with_errors=items_with_errors_count,
            items_dropped=items_dropped_count,
        )

        # errors & fields
        fields_count = sum(self.analyzer.search("fields$").values())
        self.errors = ErrorsInfo(items_count)
        self.fields = FieldErrorsInfo(
            fields_count=fields_count, items_count=items_count
        )

        field_errors = self.analyzer.search(
            "fields/errors/([^/]+)$", include_matches=True
        )
        for _, error in field_errors.values():
            field_errors_per_field = self.analyzer.search(
                "fields/errors/%s/([^/]+)$" % error, include_matches=True
            )
            for count, field in field_errors_per_field.values():
                self.errors.add_values(key=error, subkey=field, value=count)
                self.fields.add_values(key=field, subkey=error, value=count)


class ValidationMonitorMixin(StatsMonitorMixin):
    @property
    def validation(self):
        if not hasattr(self, "_validation"):
            self._validation = ValidationInfo(self.stats)
        return self._validation

    def check_missing_required_fields(self, field_names=None, allowed_count=0):
        if not field_names:
            missing_count = self.validation.errors["missing_required_field"].count
            self._check_missing_required_count(missing_count, allowed_count)
        else:
            for field_name in field_names:
                self.check_missing_required_field(field_name, allowed_count)

    def check_missing_required_field(self, field_name, allowed_count=0):
        missing_count = (
            self.validation.fields[field_name].errors["missing_required_field"].count
        )
        self._check_missing_required_count(missing_count, allowed_count)

    def _check_missing_required_count(self, missing_count, allowed_count):
        self.assertLessEqual(
            missing_count,
            allowed_count,
            msg="{count} required field{plural} are missing!{threshold_info}".format(
                count=missing_count,
                plural="" if missing_count == 1 else "s",
                threshold_info=(" (maximum allowed %d)" % allowed_count)
                if allowed_count > 0
                else "",
            ),
        )

    def check_missing_required_fields_percent(
        self, field_names=None, allowed_percent=0
    ):
        if not field_names:
            missing_percent = self.validation.errors["missing_required_field"].percent
            self._check_missing_required_percent(missing_percent, allowed_percent)
        else:
            for field_name in field_names:
                self.check_missing_required_field_percent(field_name, allowed_percent)

    def check_missing_required_field_percent(self, field_name, allowed_percent=0):
        missing_percent = (
            self.validation.fields[field_name].errors["missing_required_field"].percent
        )
        self._check_missing_required_percent(missing_percent, allowed_percent)

    def _check_missing_required_percent(self, missing_percent, allowed_percent=0):
        self.assertLessEqual(
            missing_percent,
            allowed_percent,
            msg="{percent}% of required fields are missing!{threshold_info}".format(
                percent=missing_percent * 100,
                threshold_info=(" (maximum allowed %.0f%%)" % (allowed_percent * 100))
                if allowed_percent > 0
                else "",
            ),
        )

    def check_fields_errors(self, field_names=None, errors=None, allowed_count=0):
        if not field_names:
            errors_count = self.validation.errors.count
            self._check_field_errors(errors_count, allowed_count)
        else:
            for field_name in field_names:
                self.check_field_errors(field_name, errors, allowed_count)

    def check_field_errors(self, field_name, errors=None, allowed_count=0):
        if errors:
            errors_count = sum(
                [self.validation.fields[field_name].errors[e].count for e in errors]
            )
        else:
            errors_count = self.validation.fields[field_name].errors.count
        self._check_field_errors(errors_count, allowed_count)

    def _check_field_errors(self, errors_count, allowed_count):
        self.assertLessEqual(
            errors_count,
            allowed_count,
            msg="{count} field{count_plural} {verb} validation errors!{threshold_info}".format(
                count=errors_count,
                count_plural="" if errors_count == 1 else "s",
                verb="has" if errors_count == 1 else "have",
                threshold_info=(" (maximum allowed %d)" % allowed_count)
                if allowed_count > 0
                else "",
            ),
        )

    def check_fields_errors_percent(
        self, field_names=None, errors=None, allowed_percent=0
    ):
        if not field_names:
            errors_percent = self.validation.errors.percent
            self._check_field_errors_percent(errors_percent, allowed_percent)
        else:
            for field_name in field_names:
                self.check_field_errors_percent(field_name, errors, allowed_percent)

    def check_field_errors_percent(self, field_name, errors=None, allowed_percent=0):
        if errors:
            errors_percent = sum(
                [self.validation.fields[field_name].errors[e].percent for e in errors]
            )
        else:
            errors_percent = self.validation.fields[field_name].errors.percent
        self._check_field_errors_percent(errors_percent, allowed_percent)

    def _check_field_errors_percent(self, errors_percent, allowed_percent):
        self.assertLessEqual(
            errors_percent,
            allowed_percent,
            msg="{percent}% of fields have validation errors!{threshold_info}".format(
                percent=errors_percent * 100,
                threshold_info=(" (maximum allowed %.0f%%)" % (allowed_percent * 100))
                if allowed_percent > 0
                else "",
            ),
        )
