from spidermon.actions import Action
from spidermon import settings


class DummyAction(Action):
    def run(self, result):
        pass


ACTIONS = [
    DummyAction(),
    DummyAction(),
    DummyAction(),
]

ACTIONS_AS_TUPLE2 = [
    ('A', DummyAction()),
    ('B', DummyAction()),
    ('C', DummyAction()),
]

ACTIONS_AS_TUPLE3 = [
    ('Always',    DummyAction(), settings.CHECK_STATE_ALWAYS),
    ('On Passed', DummyAction(), settings.CHECK_STATE_PASSED),
    ('On Failed', DummyAction(), settings.CHECK_STATE_FAILED),
    ('On Error',  DummyAction(), settings.CHECK_STATE_ERROR),
]