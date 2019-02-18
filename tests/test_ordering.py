from __future__ import absolute_import
from .fixtures.ordering import *

SUITE_SEQUENCES = [
    # ------------------------------------------------------------------------------------------------------------
    # monitor sequence                                      expected sequence
    # ------------------------------------------------------------------------------------------------------------
    # Unordered: should follow same insertion order (FIFO)
    ([Unordered.A, Unordered.B], [Unordered.A, Unordered.B]),
    ([Unordered.B, Unordered.A], [Unordered.B, Unordered.A]),
    ([Unordered.C, Unordered.D], [Unordered.C, Unordered.D]),
    ([Unordered.D, Unordered.C], [Unordered.D, Unordered.C]),
    (
        [Unordered.A, Unordered.B, Unordered.C, Unordered.D],
        [Unordered.A, Unordered.B, Unordered.C, Unordered.D],
    ),
    (
        [Unordered.D, Unordered.C, Unordered.B, Unordered.A],
        [Unordered.D, Unordered.C, Unordered.B, Unordered.A],
    ),
    (
        [Unordered.C, Unordered.B, Unordered.A, Unordered.D],
        [Unordered.C, Unordered.B, Unordered.A, Unordered.D],
    ),
    (
        [Unordered.A, Unordered.A, Unordered.B, Unordered.B],
        [Unordered.A, Unordered.A, Unordered.B, Unordered.B],
    ),
    (
        [Unordered.C, Unordered.C, Unordered.B, Unordered.B],
        [Unordered.C, Unordered.C, Unordered.B, Unordered.B],
    ),
    # Ordered: should follow decorators order (A, B, C, D)
    ([Ordered.A, Ordered.B], [Ordered.A, Ordered.B]),
    ([Ordered.B, Ordered.A], [Ordered.A, Ordered.B]),
    ([Ordered.C, Ordered.D], [Ordered.C, Ordered.D]),
    ([Ordered.D, Ordered.C], [Ordered.C, Ordered.D]),
    (
        [Ordered.A, Ordered.B, Ordered.C, Ordered.D],
        [Ordered.A, Ordered.B, Ordered.C, Ordered.D],
    ),
    (
        [Ordered.D, Ordered.C, Ordered.B, Ordered.A],
        [Ordered.A, Ordered.B, Ordered.C, Ordered.D],
    ),
    (
        [Ordered.C, Ordered.B, Ordered.A, Ordered.D],
        [Ordered.A, Ordered.B, Ordered.C, Ordered.D],
    ),
    (
        [Ordered.A, Ordered.A, Ordered.B, Ordered.B],
        [Ordered.A, Ordered.A, Ordered.B, Ordered.B],
    ),
    (
        [Ordered.C, Ordered.C, Ordered.B, Ordered.B],
        [Ordered.B, Ordered.B, Ordered.C, Ordered.C],
    ),
]

METHOD_SEQUENCES = [
    # --------------------------------------------------------------
    # monitor class                 expected methods sequence
    # --------------------------------------------------------------
    (UnorderedMethodsMonitor, ["test_a", "test_b", "test_c"]),
    (OrderedMethodsMonitor, ["test_c", "test_b", "test_a"]),
    (EqualOrderedMethodsMonitor, ["test_a", "test_b", "test_c"]),
]


def test_suite_ordering():
    for monitors_sequence, expected_sequence in SUITE_SEQUENCES:
        suite = MonitorSuite()
        suite.add_monitors(monitors_sequence)
        sequence = [_extract_monitor_class(m) for m in suite]
        assert sequence == expected_sequence


def test_method_ordering():
    for monitor_class, expected_sequence in METHOD_SEQUENCES:
        suite = MonitorSuite()
        suite.add_monitor(monitor_class)
        sequence = [m.method_name for m in suite.all_monitors]
        assert sequence == expected_sequence


def _extract_monitor_class(suite):
    if suite.__class__ == MonitorSuite:
        return _extract_monitor_class(suite._tests[0])
    else:
        return suite.__class__
