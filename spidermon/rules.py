import six

from .context import create_context_dict
from .exceptions import InvalidExpression


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
        self.call = call

    @property
    def name(self):
        return self.call.func_name

    def check(self, **context_params):
        return self.call(**context_params)


class PythonExpressionRule(Rule):
    """
    Python expression rule. Must be initialiazed with string containing a valid python expression.
    Context variables will be passed when evaluating.
    Example:
    'stats.scraped_items > 100'
    """
    __rule_type__ = 'python_expression'

    def __init__(self, expression):
        self.check_valid_expression(expression)
        self.expression = expression

    def check(self, **context_params):
        return eval(self.expression, context_params)

    def check_valid_expression(self, expression):
        if not isinstance(expression, six.string_types):
            raise InvalidExpression('Python expressions must be defined as strings')
        if not expression:
            raise InvalidExpression('Empty python expression')
