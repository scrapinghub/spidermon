from spidermon.core.actions import Action
from spidermon.exceptions import SkipAction
from unittest.mock import MagicMock


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
