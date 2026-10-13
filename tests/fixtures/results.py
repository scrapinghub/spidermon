import unittest

from spidermon import Monitor
from spidermon.core.actions import Action
from spidermon.exceptions import SkipAction


class PassingMonitor(Monitor):
    def test_pass(self) -> None:
        pass


class AllStatusesMonitor(Monitor):
    # Methods run in alphabetical order, one per monitor status.
    def test_a_success(self) -> None:
        pass

    def test_b_failure(self) -> None:
        self.fail("boom")

    def test_c_error(self) -> None:
        raise ValueError("kaboom")

    def test_d_skipped(self) -> None:
        self.skipTest("not today")

    @unittest.expectedFailure
    def test_e_expected_failure(self) -> None:
        self.fail("expected")

    @unittest.expectedFailure
    def test_f_unexpected_success(self) -> None:
        pass


class SuccessfulAction(Action):
    def run_action(self) -> None:
        pass


class SkippedAction(Action):
    def run_action(self) -> None:
        raise SkipAction("nothing to do")


class FailingAction(Action):
    def run_action(self) -> None:
        raise ValueError("action boom")
