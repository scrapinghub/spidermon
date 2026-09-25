from unittest.mock import MagicMock

import pytest

from spidermon.core.actions import Action
from spidermon.exceptions import NotConfigured, SkipAction


def test_action_success() -> None:
    class TestAction(Action):
        def run_action(self) -> None:
            pass

    result_mock = MagicMock()
    action = TestAction()

    action.run(result_mock, MagicMock())

    result_mock.add_action_success.assert_called()


def test_action_fail() -> None:
    class TestAction(Action):
        def run_action(self) -> None:
            raise RuntimeError

    result_mock = MagicMock()
    action = TestAction()

    action.run(result_mock, MagicMock())

    result_mock.add_action_error.assert_called()
    result_mock.add_action_success.assert_not_called()


def test_action_skip() -> None:
    class TestAction(Action):
        def run_action(self) -> None:
            raise SkipAction("Test")

    result_mock = MagicMock()
    action = TestAction()

    action.run(result_mock, MagicMock())

    result_mock.add_action_skip.assert_called()


def test_fallback_action() -> None:
    fallback_mock = MagicMock()

    class TestAction(Action):
        fallback = fallback_mock

        def run_action(self) -> None:
            raise RuntimeError

    action = TestAction()
    action.run(MagicMock(), MagicMock())

    fallback_mock.assert_called()
    fallback_mock().run.assert_called()


def test_fallback_skip_action() -> None:
    # fallback not called for SkipAction exception
    fallback_mock = MagicMock()

    class TestAction(Action):
        fallback = fallback_mock

        def run_action(self) -> None:
            raise SkipAction("Test")

    action = TestAction()

    action.run(MagicMock(), MagicMock())
    fallback_mock().run.assert_not_called()


def test_fallback_not_configured() -> None:
    # raises not configured error for unconfigured fallback actions
    fallback_mock = MagicMock()
    fallback_mock.side_effect = NotConfigured

    class TestAction(Action):
        fallback = fallback_mock

        def run_action(self) -> None:
            pass

    with pytest.raises(NotConfigured):
        TestAction()
