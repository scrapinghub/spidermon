from spidermon.utils.commands import (
    build_monitors_strings,
    enable_spidermon,
    get_settings_path,
    is_setting_setup,
    is_spidermon_enabled,
    update_settings,
)

import pytest
import spidermon
import unittest


MODULE_MONITOR = {"TestMonitor": "path.to.monitor"}

EXPECTED_IMPORT_STRING = "from path.to.monitor import TestMonitor"
EXPECTED_MONITOR_STRING = "[TestMonitor]"


def test_should_return_imports_string():
    monitor_string, import_string = build_monitors_strings(MODULE_MONITOR)
    assert import_string == EXPECTED_IMPORT_STRING


def test_should_return_monitors_string():
    monitor_string, import_string = build_monitors_strings(MODULE_MONITOR)
    assert monitor_string == EXPECTED_MONITOR_STRING


def test_should_include_spidermon_on_settings():
    ...


def test_should_update_with_spidermon_extension():
    ...


def test_should_include_spidermon_extension():
    ...


def test_should_return_settings_file_path():
    ...


def test_should_return_spidermon_status():
    ...


def test_should_write_to_settings_file():
    ...
