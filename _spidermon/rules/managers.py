import inspect
import traceback

from spidermon.testing import TestCase
from spidermon.exceptions import InvalidRuleDefinition
from spidermon import settings

from .definitions import RuleDefinition
from .results import RuleCheckResult


class RulesManager(object):
    def __init__(self, rules=None):
        self.definitions = []
        for rule in rules or []:
            self.add_rule(rule)

    def _add_definition(self, definition):
        self.definitions.append(definition)

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
        return [self._check_rule(d, stats) for d in self.definitions]

    def _check_rule(self, definition, stats):
        result = RuleCheckResult(definition=definition)
        try:
            check_result = definition.rule.run_check(stats)
            result.state = settings.CHECK_STATE_PASSED if check_result else settings.CHECK_STATE_FAILED
        except Exception, e:
            result.state = settings.CHECK_STATE_ERROR
            result.error_message = str(e)
            result.error_traceback = traceback.format_exc()
        return result

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
        self.add_rule(rule=rule, name=name, level=level)



