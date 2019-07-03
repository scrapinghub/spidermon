import pytest

from spidermon.contrib.monitors.mixins import ValidationMonitorMixin
from spidermon.contrib.scrapy.monitors import BaseScrapyMonitor
from spidermon.data import Data


stats = {
    'spidermon/validation/fields': 100,
    'spidermon/validation/fields/errors': 20,
    'spidermon/validation/fields/errors/missing_required_field': 15,
    'spidermon/validation/fields/errors/missing_required_field/field2': 5,
    'spidermon/validation/fields/errors/missing_required_field/field3': 10,
    'spidermon/validation/fields/errors/': 10,
    'spidermon/validation/items': 10,
}


class DummyValidationMonitor(BaseScrapyMonitor, ValidationMonitorMixin):
    def __init__(self, stats, methodName="runTest", name=None):
        super(DummyValidationMonitor, self).__init__(methodName, name)
        self.data = Data({'stats': stats})
        self.new_behavior = True

    def runTest(self):
        pass


def test_check_missing_required_fields_no_fields():
    monitor = DummyValidationMonitor(stats)
    msg = """
Required fields are missing:
Required field field2 is missing in 5 items!
Required field field3 is missing in 10 items!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields()


def test_check_missing_required_fields_one_field():
    monitor = DummyValidationMonitor(stats)
    msg = """
Required fields are missing:
Required field field2 is missing in 5 items!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields(field_names=['field2'])


def test_check_missing_required_fields_multiple_fields():
    monitor = DummyValidationMonitor(stats)
    msg = """
Required fields are missing:
Required field field2 is missing in 5 items!
Required field field3 is missing in 10 items!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields(field_names=['field2', 'field3'])


def test_check_missing_required_fields_no_fields_old():
    monitor = DummyValidationMonitor(stats)
    monitor.new_behavior = False
    msg = "15 required fields are missing!"
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields()


def check_missing_required_field():
    monitor = DummyValidationMonitor(stats)
    msg = "Required field field2 is missing in 5 items!"
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_field(field_name='field2')


def test_check_missing_required_fields_percent_no_fields():
    monitor = DummyValidationMonitor(stats)
    msg = """
Required fields are missing:
50.0% of required field field2 are missing!
100.0% of required field field3 are missing!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields_percent()


def test_check_missing_required_fields_percent_one_field():
    monitor = DummyValidationMonitor(stats)
    msg = """
Required fields are missing:
50.0% of required field field2 are missing!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields_percent(field_names=['field2'])


def test_check_missing_required_fields_percent_multiple_fields():
    monitor = DummyValidationMonitor(stats)
    msg = """
Required fields are missing:
50.0% of required field field2 are missing!
100.0% of required field field3 are missing!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields_percent(field_names=['field2', 'field3'])


def test_check_missing_required_fields_percent_no_fields_old():
    monitor = DummyValidationMonitor(stats)
    monitor.new_behavior = False
    msg = "150.0% of required fields are missing!"
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields_percent()


def check_missing_required_field_percent():
    monitor = DummyValidationMonitor(stats)
    msg = "50.0% of required field field2 are missing!"
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_field_percent(field_name='field2')


def test_check_fields_errors_no_fields():
    monitor = DummyValidationMonitor(stats)
    msg = """
There are field errors:
Field field2 has 5 validation errors!
Field field3 has 10 validation errors!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors()


def test_check_fields_errors_one_field():
    monitor = DummyValidationMonitor(stats)
    msg = """
There are field errors:
Field field2 has 5 validation errors!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors(field_names=['field2'])


def test_check_fields_errors_multiple_fields():
    monitor = DummyValidationMonitor(stats)
    msg = """
There are field errors:
Field field2 has 5 validation errors!
Field field3 has 10 validation errors!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors(field_names=['field2', 'field3'])


def test_check_fields_errors_no_fields_old():
    monitor = DummyValidationMonitor(stats)
    monitor.new_behavior = False
    msg = "15 fields have validation errors!"
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors()


def test_check_field_errors():
    monitor = DummyValidationMonitor(stats)
    msg = "Field field2 has 5 validation errors!"
    with pytest.raises(AssertionError, match=msg):
        monitor.check_field_errors(field_name='field2')


def test_check_fields_errors_percent_no_fields():
    monitor = DummyValidationMonitor(stats)
    msg = """
There are field errors:
50.0% of field field2 have validation errors!
100.0% of field field3 have validation errors!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors_percent()


def test_check_fields_errors_percent_one_field():
    monitor = DummyValidationMonitor(stats)
    msg = """
There are field errors:
50.0% of field field2 have validation errors!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors_percent(field_names=['field2'])


def test_check_fields_errors_percent_multiple_fields():
    monitor = DummyValidationMonitor(stats)
    msg = """
There are field errors:
50.0% of field field2 have validation errors!
100.0% of field field3 have validation errors!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors_percent(field_names=['field2', 'field3'])


def test_check_fields_errors_percent_no_fields_old():
    monitor = DummyValidationMonitor(stats)
    monitor.new_behavior = False
    msg = "150.0% of fields have validation errors!"
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors_percent()


def test_check_field_errors_percent():
    monitor = DummyValidationMonitor(stats)
    msg = "50.0% of field field2 have validation errors!"
    with pytest.raises(AssertionError, match=msg):
        monitor.check_field_errors_percent(field_name='field2')
