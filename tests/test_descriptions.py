from __future__ import absolute_import
from .fixtures.descriptions import *

MONITOR_DESCRIPTIONS = [
    # --------------------------------------------------------------
    # monitor class                 description
    # --------------------------------------------------------------
    (NotDescriptedMonitor, ""),
    (DocstringDescriptedMonitor, "docstring monitor description"),
    (DescoratedDescriptedMonitor, "decorator monitor description"),
    (DescoratedDescriptedMonitor2, "decorator monitor description"),
]

SUITE_DESCRIPTIONS = [
    # --------------------------------------------------------------
    # suite class                   description
    # --------------------------------------------------------------
    (NotDescriptedSuite, ""),
    (DocstringDescriptedSuite, "docstring suite description"),
    (DescoratedDescriptedSuite, "decorator suite description"),
    (DescoratedDescriptedSuite2, "decorator suite description"),
]

METHOD_DESCRIPTIONS = [
    # ---------------------------------------------------------------------------------------------
    # monitor class                 method name                     description
    # ---------------------------------------------------------------------------------------------
    (DescriptedMethodsMonitor, "test_not_descripted", ""),
    (
        DescriptedMethodsMonitor,
        "test_docstring_descripted",
        "docstring method description",
    ),
    (
        DescriptedMethodsMonitor,
        "test_decorator_descripted",
        "decorator method description",
    ),
    (
        DescriptedMethodsMonitor,
        "test_decorator_descripted2",
        "decorator method description",
    ),
]


def test_monitor_descriptions():
    for monitor_class, description in MONITOR_DESCRIPTIONS:
        assert monitor_class().monitor_description == description


def test_suite_descriptions():
    for suite_class, description in SUITE_DESCRIPTIONS:
        assert suite_class().description == description


def test_method_descriptions():
    for monitor_class, method_name, description in METHOD_DESCRIPTIONS:
        assert monitor_class(method_name).method_description == description
