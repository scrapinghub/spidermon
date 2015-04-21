import six

from .context import create_context_dict
from .exceptions import InvalidExpression, InvalidCallable
from .python import Interpreter


class Rule(object):
    """
    Base class for rules
    """
    __rule_type__ = 'rule'

    def __str__(self):
        return self.__class__.__name__

    @property
    def type(self):
        return self.__rule_type__

    @property
    def name(self):
        return self.type

    def run_check(self, stats):
        context_params = create_context_dict(stats)
        return bool(self.check(**context_params))

    def check(self, stats):
        raise NotImplementedError


class CallableRule(Rule):
    """
    Callable rule. Must be initialiazed with a callable that will be used for checking
    """
    __rule_type__ = 'callable'

    def __init__(self, call):
        self._assert_callable(call)
        self.call = call

    @property
    def name(self):
        return self.call.func_name

    def check(self, **context_params):
        return self.call(**context_params)

    def _assert_callable(self, call):
        if not hasattr(call, '__call__'):
            raise InvalidCallable('Not a valid callable: %s' % call.__class__.__name__)


class PythonExpressionRule(Rule):
    """
    Python expression rule. Must be initialiazed with string containing a valid python expression.
    Context variables will be passed when evaluating.
    Example:
    'stats.scraped_items > 100'
    """
    __rule_type__ = 'python_expression'

    def __init__(self, expression):
        self.interpreter = Interpreter()
        self._assert_valid_expression(expression)
        self.expression = expression

    def check(self, **context_params):
        return self.interpreter.eval(self.expression, context_params)

    def _assert_valid_expression(self, expression):
        self.interpreter.check(expression)
