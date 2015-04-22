import six

from spidermon.serialization import JSONSerializable
from spidermon.exceptions import InvalidRuleDefinition, InvalidRuleLevel
from spidermon import settings

from . import Rule, CallableRule, TestCaseRule, PythonExpressionRule


class RuleDefinition(JSONSerializable):
    def __init__(self, rule, name=None, level=None, test_case=None):
        self.rule = self._get_rule(rule, test_case)
        self.name = self._get_name(name)
        self.level = self._get_level(level)

    @property
    def type(self):
        return self.rule.type

    def _get_rule(self, rule, test_case):
        if isinstance(rule, Rule):
            return rule
        elif hasattr(rule, '__call__'):
            if test_case:
                return TestCaseRule(rule, test_case)
            else:
                return CallableRule(rule)
        elif isinstance(rule, six.string_types):
            return PythonExpressionRule(rule)
        else:
            raise InvalidRuleDefinition('Wrong Rule definition, rules should be:\n'
                                        '- an instance of Rule/TestCase objects.\n'
                                        '- a callable.\n'
                                        '- a string containing an evaluable python expression.')

    def _get_name(self, name):
        return name or self.rule.name

    def _get_level(self, level):
        if level and level not in settings.LEVELS:
            raise InvalidRuleLevel("Invalid rule severity level '%s'" % level)
        return level or settings.DEFAULT_LEVEL

    def as_dict(self):
        data = {
            'name': self.name,
            'type': self.rule.type,
            'level': self.level,
        }
        return data