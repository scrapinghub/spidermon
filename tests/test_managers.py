import pytest
import json

from spidermon.rules import CallableRule, PythonExpressionRule, TestCaseRule
from spidermon.managers import RulesManager
from spidermon.exceptions import InvalidRuleDefinition, InvalidRuleLevel

from fixtures.rules import *
from fixtures.stats import *
from fixtures.json import *


def test_errors():
    with pytest.raises(InvalidRuleDefinition):
        RulesManager([()])

    with pytest.raises(InvalidRuleDefinition):
        RulesManager([None])

    with pytest.raises(InvalidRuleDefinition):
        RulesManager([10])

    with pytest.raises(InvalidRuleLevel):
        RulesManager([('rule', SimpleRule, 'WRONG LEVEL')])

    with pytest.raises(InvalidRuleDefinition):
        RulesManager([('rule', SimpleRule, settings.LEVEL_NORMAL, None)])


def test_rules():
    manager = RulesManager(RULES)
    _test_definitions(
        definitions=manager.definitions,
        values=(
            # (type,                class,                  level,                  name)
            ('rule',                SimpleRule,             settings.LEVEL_NORMAL,  'rule'),
            ('python_expression',   PythonExpressionRule,   settings.LEVEL_NORMAL,  'python_expression'),
            ('callable',            CallableRule,           settings.LEVEL_NORMAL,  '<lambda>'),
            ('callable',            CallableRule,           settings.LEVEL_NORMAL,  'a_function'),
            ('test_case',           TestCaseRule,           settings.LEVEL_NORMAL,  'ATestCase.test_method_a'),
            ('test_case',           TestCaseRule,           settings.LEVEL_NORMAL,  'ATestCase.test_method_b'),
        ),
    )


def test_rules_as_tuple2():
    manager = RulesManager(RULES_AS_TUPLE2)
    _test_definitions(
        definitions=manager.definitions,
        values=(
            # (type,                class,                  level,                  name)
            ('rule',                SimpleRule,             settings.LEVEL_NORMAL,  'RULE_OBJECT'),
            ('python_expression',   PythonExpressionRule,   settings.LEVEL_NORMAL,  'RULE_EXPRESSION'),
            ('callable',            CallableRule,           settings.LEVEL_NORMAL,  'RULE_LAMBDA'),
            ('callable',            CallableRule,           settings.LEVEL_NORMAL,  'RULE_FUNCTION'),
            ('test_case',           TestCaseRule,           settings.LEVEL_NORMAL,  'RULE_TESTCASE.test_method_a'),
            ('test_case',           TestCaseRule,           settings.LEVEL_NORMAL,  'RULE_TESTCASE.test_method_b'),
        ),
    )


def test_rules_as_tuple3():
    manager = RulesManager(RULES_AS_TUPLE3)
    _test_definitions(
        definitions=manager.definitions,
        values=(
            # (type,                class,                  level,                name)
            ('rule',                SimpleRule,             settings.LEVEL_HIGH,  'RULE_OBJECT'),
            ('python_expression',   PythonExpressionRule,   settings.LEVEL_HIGH,  'RULE_EXPRESSION'),
            ('callable',            CallableRule,           settings.LEVEL_HIGH,  'RULE_LAMBDA'),
            ('callable',            CallableRule,           settings.LEVEL_HIGH,  'RULE_FUNCTION'),
            ('test_case',           TestCaseRule,           settings.LEVEL_HIGH,  'RULE_TESTCASE.test_method_a'),
            ('test_case',           TestCaseRule,           settings.LEVEL_HIGH,  'RULE_TESTCASE.test_method_b'),
        ),
    )


def _test_definitions(definitions, values):
    for definition, rule_values in zip(definitions, values):
        rule_type, rule_class, rule_level, rule_name = rule_values
        assert isinstance(definition.rule, rule_class)
        assert rule_type == definition.type
        assert rule_level == definition.level
        assert rule_name == definition.name


def test_json():
    _test_json(
        rules=RULES_AS_TUPLE3,
        stats=STATS_A,
        expected_json_results=JSON_RESULTS_PASS,
    )
    _test_json(
        rules=RULES_AS_TUPLE3,
        stats=STATS_B,
        expected_json_results=JSON_RESULTS_FAIL,
    )
    _test_json(
        rules=RULES_AS_TUPLE3,
        stats=STATS_EMPTY,
        expected_json_results=JSON_RESULTS_ERROR,
    )


def _clean_json_results(results):
    cleaned_results = []
    for r in results:
        obj = json.loads(r.json())
        if 'error' in obj and 'traceback' in obj['error']:
            del obj['error']['traceback']
        cleaned_results.append(obj)
    return json.dumps(cleaned_results, sort_keys=True, indent=4)


def _test_json(rules, stats, expected_json_results):
    manager = RulesManager(rules)
    results = manager.check_rules(stats)
    cleaned_results = _clean_json_results(results)
    cleaned_expected_results = json.dumps(json.loads(expected_json_results), sort_keys=True, indent=4)
    assert cleaned_results == cleaned_expected_results

