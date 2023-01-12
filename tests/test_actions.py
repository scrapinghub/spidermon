from spidermon.core.actions import Action
from spidermon.exceptions import NotConfigured, SkipAction
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
    fallback_mock = MagicMock()

    class TestAction(Action):
        fallback = fallback_mock

        def run_action(self):
            raise Exception

    action = TestAction()
    action.run(MagicMock(), MagicMock())

    fallback_mock.assert_called()
    fallback_mock().run.assert_called()


def test_fallback_skip_action():
    # fallback not called for SkipAction exception
    fallback_mock = MagicMock()

    class TestAction(Action):
        fallback = fallback_mock

        def run_action(self):
            raise SkipAction("Test")

    action = TestAction()

    action.run(MagicMock(), MagicMock())
    fallback_mock().run.assert_not_called()


def test_fallback_not_configured():
    # raises not configured error for unconfigured fallback actions
    fallback_mock = MagicMock()
    fallback_mock.side_effect = NotConfigured

    class TestAction(Action):
        fallback = fallback_mock

        def run_action(self):
            pass

    try:
        TestAction()
    except NotConfigured:
        assert True
    else:
        assert False
