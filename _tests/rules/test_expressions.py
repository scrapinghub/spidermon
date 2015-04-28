import pytest
import unittest

from spidermon.python import Interpreter, InvalidExpression
from spidermon.context import create_context_dict

from tests.fixtures.expressions import *
from tests.fixtures.stats import *


class ExpressionBase(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()

    def _test_expression(self, expression):
        self.interpreter.check(expression)


class ExpressionInvalid(ExpressionBase):
    def test_syntax_error(self):
        for exp in SYNTAXERROR_EXPRESSIONS:
            with pytest.raises(SyntaxError):
                self._test_expression(exp)

    def test_invalid_expressions(self):
        for exp in INVALID_EXPRESSIONS:
            with pytest.raises(InvalidExpression):
                self._test_expression(exp)


class ExpressionValid(ExpressionBase):
    def test_valid_expressions(self):
        for exp in VALID_EXPRESSIONS:
            self._test_expression(exp)


class ExpressionEval(ExpressionBase):
    def test_evaluated_expressions(self):
        context = create_context_dict(STATS_TO_EVALUATE)
        interpreter = Interpreter()
        for expression, result in EXPRESSIONS_TO_EVALUATE:
            assert result == interpreter.eval(expression, context), \
                'Expression fails: "%s" != %s' % (expression, result)
