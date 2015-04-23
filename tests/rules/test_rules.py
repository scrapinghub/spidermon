import pytest

from spidermon import CallableRule, PythonExpressionRule
from spidermon.exceptions import InvalidExpression, InvalidCallable

from tests.fixtures.rules import *
from tests.fixtures.stats import *
from tests.fixtures.expressions import *


def test_base_rule():
    with pytest.raises(NotImplementedError):
        RULE_OBJECT_BASE.run_check(STATS_EMPTY)


def test_dummy_rule():
    assert RULE_OBJECT_DUMMY.run_check(STATS_EMPTY) is True


def test_simple_rule():
    _test_rule_with_stats(RULE_OBJECT_SIMPLE)


def test_not_callable():
    with pytest.raises(InvalidCallable):
        CallableRule(None)


def test_function_rule():
    rule = CallableRule(RULE_FUNCTION)
    _test_rule_with_stats(rule)


def test_lambda_rule():
    rule = CallableRule(RULE_LAMBDA)
    _test_rule_with_stats(rule)


def _test_rule_with_stats(rule):
    assert rule.run_check(STATS_A) is True  # PASSED
    assert rule.run_check(STATS_B) is False  # FAILED
    with pytest.raises(AttributeError):  # ERROR
        rule.run_check(STATS_EMPTY)


def test_python_rule():
    with pytest.raises(SyntaxError):
        for exp in SYNTAXERROR_EXPRESSIONS:
            PythonExpressionRule(exp)

    with pytest.raises(InvalidExpression):
        for exp in INVALID_EXPRESSIONS:
            PythonExpressionRule(exp)

    for exp in VALID_EXPRESSIONS:
        PythonExpressionRule(exp)

    rule = PythonExpressionRule(RULE_EXPRESSION)
    _test_rule_with_stats(rule)

    for expression, result in EXPRESSIONS_TO_EVALUATE:
        rule = PythonExpressionRule(expression)
        assert result == rule.run_check(STATS_TO_EVALUATE), \
            'Expression fails: "%s" != %s' % (expression, result)

