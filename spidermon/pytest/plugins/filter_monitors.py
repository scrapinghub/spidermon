import pytest

from spidermon import Monitor


def pytest_report_header(config):
    return "Spidermon test filtering"


@pytest.mark.trylast
def pytest_collection_modifyitems(session, config, items):
    items[:] = [item for item in items
                if not (item.cls and issubclass(item.cls, Monitor))]
