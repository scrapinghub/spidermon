import re

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
    def __init__(self, stats, correct_field_list_handling, methodName="runTest", name=None):
        super(DummyValidationMonitor, self).__init__(methodName, name)
        self.data = Data({'stats': stats})
        self.correct_field_list_handling = correct_field_list_handling

    def runTest(self):
        pass


@pytest.fixture
def monitor():
    return DummyValidationMonitor(stats, True)


@pytest.fixture
def old_monitor():
    return DummyValidationMonitor(stats, False)


def test_check_missing_required_fields_no_fields(monitor):
    msg = """
Required fields are missing:
Required field field2 is missing in 5 items!
Required field field3 is missing in 10 items!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields()
    msg = """
Required fields are missing:
Required field field3 is missing in 10 items! (maximum allowed 7)
    """.strip()
    with pytest.raises(AssertionError, match=re.escape(msg)):
        monitor.check_missing_required_fields(allowed_count=7)


def test_check_missing_required_fields_one_field(monitor):
    monitor.check_missing_required_fields(field_names=['field1'])
    msg = """
Required fields are missing:
Required field field2 is missing in 5 items!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields(field_names=['field2'])


def test_check_missing_required_fields_multiple_fields(monitor):
    msg = """
Required fields are missing:
Required field field2 is missing in 5 items!
Required field field3 is missing in 10 items!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields(field_names=['field2', 'field3'])


def test_check_missing_required_fields_no_fields_old(old_monitor):
    msg = "15 required fields are missing!"
    with pytest.raises(AssertionError, match=msg):
        old_monitor.check_missing_required_fields()


def check_missing_required_field(monitor):
    monitor.check_missing_required_field(field_name='field1')
    msg = "Required field field2 is missing in 5 items!"
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_field(field_name='field2')


def test_check_missing_required_fields_percent_no_fields(monitor):
    msg = """
Required fields are missing:
50.0% of required field field2 are missing!
100.0% of required field field3 are missing!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields_percent()
    msg = """
Required fields are missing:
100.0% of required field field3 are missing! (maximum allowed 70%)
    """.strip()
    with pytest.raises(AssertionError, match=re.escape(msg)):
        monitor.check_missing_required_fields_percent(allowed_percent=0.7)


def test_check_missing_required_fields_percent_one_field(monitor):
    monitor.check_missing_required_fields_percent(field_names=['field1'])
    msg = """
Required fields are missing:
50.0% of required field field2 are missing!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields_percent(field_names=['field2'])


def test_check_missing_required_fields_percent_multiple_fields(monitor):
    msg = """
Required fields are missing:
50.0% of required field field2 are missing!
100.0% of required field field3 are missing!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_fields_percent(field_names=['field2', 'field3'])


def test_check_missing_required_fields_percent_no_fields_old(old_monitor):
    msg = "150.0% of required fields are missing!"
    with pytest.raises(AssertionError, match=msg):
        old_monitor.check_missing_required_fields_percent()


def check_missing_required_field_percent(monitor):
    monitor.check_missing_required_field_percent(field_name='field1')
    msg = "50.0% of required field field2 are missing!"
    with pytest.raises(AssertionError, match=msg):
        monitor.check_missing_required_field_percent(field_name='field2')


def test_check_fields_errors_no_fields(monitor):
    msg = """
There are field errors:
Field field2 has 5 validation errors!
Field field3 has 10 validation errors!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors()
    msg = """
There are field errors:
Field field3 has 10 validation errors! (maximum allowed 7)
    """.strip()
    with pytest.raises(AssertionError, match=re.escape(msg)):
        monitor.check_fields_errors(allowed_count=7)


def test_check_fields_errors_one_field(monitor):
    monitor.check_fields_errors(field_names=['field1'])
    msg = """
There are field errors:
Field field2 has 5 validation errors!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors(field_names=['field2'])


def test_check_fields_errors_multiple_fields(monitor):
    msg = """
There are field errors:
Field field2 has 5 validation errors!
Field field3 has 10 validation errors!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors(field_names=['field2', 'field3'])


def test_check_fields_errors_no_fields_old(old_monitor):
    msg = "15 fields have validation errors!"
    with pytest.raises(AssertionError, match=msg):
        old_monitor.check_fields_errors()


def test_check_field_errors(monitor):
    monitor.check_field_errors(field_name='field1')
    msg = "Field field2 has 5 validation errors!"
    with pytest.raises(AssertionError, match=msg):
        monitor.check_field_errors(field_name='field2')


def test_check_fields_errors_percent_no_fields(monitor):
    msg = """
There are field errors:
50.0% of field field2 have validation errors!
100.0% of field field3 have validation errors!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors_percent()
    msg = """
There are field errors:
100.0% of field field3 have validation errors! (maximum allowed 70%)
    """.strip()
    with pytest.raises(AssertionError, match=re.escape(msg)):
        monitor.check_fields_errors_percent(allowed_percent=0.7)


def test_check_fields_errors_percent_one_field(monitor):
    monitor.check_fields_errors_percent(field_names=['field1'])
    msg = """
There are field errors:
50.0% of field field2 have validation errors!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors_percent(field_names=['field2'])


def test_check_fields_errors_percent_multiple_fields(monitor):
    msg = """
There are field errors:
50.0% of field field2 have validation errors!
100.0% of field field3 have validation errors!
    """.strip()
    with pytest.raises(AssertionError, match=msg):
        monitor.check_fields_errors_percent(field_names=['field2', 'field3'])


def test_check_fields_errors_percent_no_fields_old(old_monitor):
    msg = "150.0% of fields have validation errors!"
    with pytest.raises(AssertionError, match=msg):
        old_monitor.check_fields_errors_percent()


def test_check_field_errors_percent(monitor):
    monitor.check_field_errors_percent(field_name='field1')
    msg = "50.0% of field field2 have validation errors!"
    with pytest.raises(AssertionError, match=msg):
        monitor.check_field_errors_percent(field_name='field2')
