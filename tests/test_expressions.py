import pytest

from spidermon.python import Interpreter
from spidermon.exceptions import InvalidExpression
from spidermon.stats import Stats

from fixtures.expressions import *
from fixtures.stats import STATS_TO_EVALUATE


@pytest.fixture
def interpreter():
    return Interpreter()


def test_syntax_errors(interpreter):
    for expression in SYNTAXERROR_EXPRESSIONS:
        with pytest.raises(SyntaxError):
            interpreter.check(expression)


def test_invalid_expressions(interpreter):
    for expression in INVALID_EXPRESSIONS:
        with pytest.raises(InvalidExpression):
            interpreter.check(expression)


def test_valid_expressions(interpreter):
    for expression in VALID_EXPRESSIONS:
        interpreter.check(expression)


def test_evaluated_expressions(interpreter):
    context = {'stats': Stats(STATS_TO_EVALUATE)}
    for expression, result in EXPRESSIONS_TO_EVALUATE:
        assert result == interpreter.eval(expression, context), \
            'Expression fails: "%s" != %s' % (expression, result)
