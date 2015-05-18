from spidermon.contrib.stats.counters import PercentCounter, DictPercentCounter, AttributeDictPercentCounter
from spidermon.contrib.stats.analyzer import StatsAnalyzer
from spidermon.contrib.scrapy.stats import STATS_DEFAULT_VALIDATION_PREFIX
from spidermon.core.monitors import StatsMonitor


class MetaDictPercentCounter(DictPercentCounter):
    def add_values(self, key, subkey, value):
        if key not in self._dict:
            self._create_item(key)
        self[key].add_value(subkey, value)


class ErrorsDictPercentCounter(AttributeDictPercentCounter):
    __attribute_dict_name__ = 'fields'


class ErrorsInfo(MetaDictPercentCounter):
    __items_class__ = ErrorsDictPercentCounter


class FieldErrorsDictPercentCounter(AttributeDictPercentCounter):
    __attribute_dict_name__ = 'errors'


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
        self.analyzer = StatsAnalyzer(stats=stats, prefix=prefix or STATS_DEFAULT_VALIDATION_PREFIX)

        # items
        items_count = sum(self.analyzer.search('items$').values())
        items_with_errors_count = sum(self.analyzer.search('items/errors$').values())
        items_dropped_count = sum(self.analyzer.search('items/dropped$').values())
        self.items = ItemsInfo(
            items_count=items_count,
            items_with_errors=items_with_errors_count,
            items_dropped=items_dropped_count)

        # errors & fields
        fields_count = sum(self.analyzer.search('fields$').values())
        self.errors = ErrorsInfo(items_count)
        self.fields = FieldErrorsInfo(fields_count=fields_count, items_count=items_count)

        field_errors = self.analyzer.search('fields/errors/([^/]+)$', include_matches=True)
        for _, error in field_errors.values():
            field_errors_per_field = self.analyzer.search('fields/errors/%s/([^/]+)$' % error, include_matches=True)
            for count, field in field_errors_per_field.values():
                self.errors.add_values(key=error, subkey=field, value=count)
                self.fields.add_values(key=field, subkey=error, value=count)


class ValidationMonitor(StatsMonitor):
    def __init__(self, methodName='runTest', name=None):
        super(ValidationMonitor, self).__init__(methodName, name)
        self.validation = None

    def init_data(self, data):
        super(ValidationMonitor, self).init_data(data)
        self.validation = ValidationInfo(self.stats)
