from spidermon.core.actions import Action
from spidermon.exceptions import SkipAction
from unittest.mock import MagicMock


def test_action_success():
    class TestAction(Action):
        def run_action(self):
            pass

    result_mock = MagicMock()
    action = TestAction()

    action.run(result_mock, MagicMock())

    result_mock.add_action_success.assert_called()


def test_action_fail():
    class TestAction(Action):
        def run_action(self):
            raise Exception

    result_mock = MagicMock()
    action = TestAction()

    action.run(result_mock, MagicMock())

    result_mock.add_action_error.assert_called()
    result_mock.add_action_success.assert_not_called()


def test_action_skip():
    class TestAction(Action):
        def run_action(self):
            raise SkipAction("Test")

    result_mock = MagicMock()
    action = TestAction()

    action.run(result_mock, MagicMock())

    result_mock.add_action_skip.assert_called()


def test_fallback_action():
    class TestAction(Action):
        fallback = MagicMock()

        def run_action(self):
            raise Exception

    action = TestAction()
    action.run(MagicMock(), MagicMock())

    action.fallback.assert_called()
    action.fallback().run.assert_called()


def test_fallback_skip_action():
    # fallback not called for SkipAction exception
    class TestAction(Action):
        fallback = MagicMock()

        def run_action(self):
            raise SkipAction("Test")

    action = TestAction()

    action.run(MagicMock(), MagicMock())
    action.fallback.assert_not_called()
