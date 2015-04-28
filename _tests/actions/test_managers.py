import pytest
import json
import jsonschema

from spidermon.actions import Action
from spidermon.actions.managers import ActionsManager
from spidermon.exceptions import InvalidActionDefinition, InvalidState
from spidermon.monitors import Monitor
from spidermon.monitors.results import MonitorResult
from spidermon.rules.managers import RulesManager
from spidermon.serialization import SpidermonJSONEncoder
from spidermon import settings

from tests.fixtures.rules import *
from tests.fixtures.actions import *
from tests.fixtures.stats import *
from tests.fixtures.schemas import *


def test_errors():
    with pytest.raises(InvalidActionDefinition):
        ActionsManager([()])

    with pytest.raises(InvalidActionDefinition):
        ActionsManager([None])

    with pytest.raises(InvalidActionDefinition):
        ActionsManager([10])

    with pytest.raises(InvalidState):
        ActionsManager([('rule', Action(), 'WRONG STATE')])

    with pytest.raises(InvalidActionDefinition):
        ActionsManager([('rule', Action(), settings.LEVEL_NORMAL, None)])


def test_rules():
    manager = ActionsManager(ACTIONS)
    _test_actions(
        actions=manager.definitions,
        values=(
            # (class,       trigger,                        name)
            (DummyAction,   settings.CHECK_STATE_ALWAYS,    'DummyAction'),
            (DummyAction,   settings.CHECK_STATE_ALWAYS,    'DummyAction'),
            (DummyAction,   settings.CHECK_STATE_ALWAYS,    'DummyAction'),
        ),
    )


def test_rules_as_tuple2():
    manager = ActionsManager(ACTIONS_AS_TUPLE2)
    _test_actions(
        actions=manager.definitions,
        values=(
            # (class,       trigger,                        name)
            (DummyAction,   settings.CHECK_STATE_ALWAYS,    'A'),
            (DummyAction,   settings.CHECK_STATE_ALWAYS,    'B'),
            (DummyAction,   settings.CHECK_STATE_ALWAYS,    'C'),
        ),
    )


def test_rules_as_tuple3():
    manager = ActionsManager(ACTIONS_AS_TUPLE3)
    _test_actions(
        actions=manager.definitions,
        values=(
            # (class,       trigger,                        name)
            (DummyAction,   settings.CHECK_STATE_ALWAYS,    'Always'),
            (DummyAction,   settings.CHECK_STATE_PASSED,    'On Passed'),
            (DummyAction,   settings.CHECK_STATE_FAILED,    'On Failed'),
            (DummyAction,   settings.CHECK_STATE_ERROR,     'On Error'),
        ),
    )


def _test_actions(actions, values):
    for definition, action_values in zip(actions, values):
        pass
        action_class, action_trigger, action_name = action_values
        assert isinstance(definition.action, action_class)
        assert action_trigger == definition.trigger
        assert action_name == definition.name


def test_json():
    _test_json(
        rules=[RULE_PASS],
        stats=STATS_A,
        actions=[('Pass',  DummyAction(), settings.CHECK_STATE_PASSED)],
        schemas=[ACTION_RESULTS_SCHEMA, ACTION_RESULTS_PROCESSED_SCHEMA],
    )
    _test_json(
        rules=[RULE_PASS],
        stats=STATS_A,
        actions=[('Fail',  DummyAction(), settings.CHECK_STATE_FAILED)],
        schemas=[ACTION_RESULTS_SCHEMA, ACTION_RESULTS_SKIPPED_SCHEMA],
    )
    _test_json(
        rules=[RULE_PASS],
        stats=STATS_A,
        actions=[('Error', Action())],
        schemas=[ACTION_RESULTS_SCHEMA, ACTION_RESULTS_ERROR_SCHEMA],
    )


def _test_json(rules, stats, actions, schemas):
    result = MonitorResult(Monitor())
    result.checks = RulesManager(rules).check_rules(stats)
    manager = ActionsManager(actions)
    results = manager.run_actions(result)
    results_json = json.dumps(results, cls=SpidermonJSONEncoder)
    results_obj = json.loads(results_json)
    for schema in schemas:
        jsonschema.validate(results_obj, schema)
