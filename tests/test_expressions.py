import pytest
import unittest


from spidermon.python import Interpreter, InvalidExpression


SYNTAXERROR_EXPRESSIONS = [
    '?',
    'a string',
    'a=',
]

INVALID_EXPRESSIONS = [
    None,
    0,
    '',
    """
    """,
    'a > b\na > b',
    'import os',
    'from os import *',
    'for i in range(10): pass',
    'def something(): pass',
    'lambda x: x',
    "del a",
    "print a",
    "raise Exception",
    "pass",
    "return",
    "yield x",

    # Assignment Operations
    "a = 1",
    "a += 1",
    "a -= 1",
    "a *= 1",
    "a /= 1",
    "a %= 1",
    "a **= 1",
    "a //= 1",
]

VALID_EXPRESSIONS = [
    # Strings
    "'single quoted string'",
    "\"double quoted string\"",
    "u'unicode single quoted string'",
    "u\"unicode double quoted string\"",

    # Numbers
    "0",
    "-10",
    "10",
    "1.0",
    "-1.0",
    "51924361L",
    "3.14j",

    # Sequences
    "[1, 2, 3]",
    "{'a': 1, 'b': 1}",
    "set()",
    "(1, 2)",
    "len(a)",

    # Constants
    "None",
    "True",
    "False",

    # Arithmetic Operations
    "-a",
    "a + 1",
    "a - 1",
    "a / 1",
    "a * 1",
    "a % 1",
    "a ** 1",
    "a // 1",

    # Comparison Operations
    "a == b",
    "a != b",
    "a <> b",
    "a > b",
    "a < b",
    "a >= b",
    "a <= b",
    "1 < a < 10",

    # Bitwise Operations
    "a & b",
    "a | b",
    "a ^ b",
    "~a",
    "a << b",
    "a >> b",

    # Logical Operations
    "a and b",
    "a or b",
    "not a",

    # Membership Operations
    "a in b",
    "a not in b",

    # Identity Operations
    "a is 10",
    "a is not 10",

    # Inline if statement
    "a if b else c",

    # Subscripting
    "a[1]",
    "a[1:2]",
    "a[1:2, 3]",

    # Comprehensions
    "[i for i in range(10)]",
    "{i: i**2 for i in range(10)}",
    "{i for i in range(10)}",
    "[n for n in range(10) if n>5]",

    # Attribute access
    "stats.scraped_items"
]


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


class Expressionvalid(ExpressionBase):
    def test_valid_expressions(self):
        for exp in VALID_EXPRESSIONS:
            self._test_expression(exp)
