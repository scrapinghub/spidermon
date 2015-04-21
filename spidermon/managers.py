import six
import inspect

from .rules import Rule, CallableRule, PythonExpressionRule, TestCaseRule
from .testing import TestCase
from .exceptions import InvalidRuleDefinition, InvalidRuleLevel
from . import settings


class RuleDefinition(object):
    def __init__(self, rule, name=None, level=None, test_case=None):
        self.rule = self._get_rule(rule, test_case)
        self.name = self._get_name(name)
        self.level = self._get_level(level)

    @property
    def type(self):
        return self.rule.type

    def __str__(self):
        return '%-20s %-23s %-9s %-20s' % (self.type, self.rule, self.level, self.name)

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


class RulesManager(object):
    def __init__(self, rules=None):
        self.definitions = []
        for rule in rules or []:
            self.add_rule(rule)

    def add_rule(self, rule, name=None, level=None):
        if isinstance(rule, tuple):
            self._add_definition_from_tuple(rule)
        elif isinstance(rule, TestCase):
            self._add_definition_from_test_case(rule, name, level)
        elif inspect.isclass(rule) and issubclass(rule, TestCase):
            self._add_definition_from_test_case(rule(), name, level)
        else:
            definition = RuleDefinition(rule, name, level)
            self._add_definition(definition)

    def check_rules(self, stats):
        for definition in self.definitions:
            passed = definition.rule.run_check(stats)
            print 'checking rule: %-30s %s' % (definition.name, 'PASSED' if passed else 'FAILED')

    def _add_definition(self, definition):
        self.definitions.append(definition)

    def _add_definition_from_test_case(self, test_case, test_case_name=None, level=None):
        for test_name, test in test_case.get_test_methods().items():
            name = '%s.%s' % (test_case_name or test_case.__class__.__name__, test_name)
            definition = RuleDefinition(test, name, level, test_case)
            self._add_definition(definition)

    def _add_definition_from_tuple(self, tuple_definition):
        level = None
        if len(tuple_definition) == 2:
            name, rule = tuple_definition
        elif len(tuple_definition) == 3:
            name, rule, level = tuple_definition
        else:
            raise InvalidRuleDefinition('Wrong Rule tuple definition, you should '
                                        'either use (name, rule) or '
                                        '(name, rule, level)')
        self.add_rule(rule, name, level)
