import six
import inspect
import traceback

from .rules import Rule, CallableRule, PythonExpressionRule, TestCaseRule
from .testing import TestCase
from .actions import Action
from .exceptions import (InvalidRuleDefinition, InvalidRuleLevel,
                         InvalidState, InvalidActionDefinition)
from .serialization import JSONSerializable
from . import settings


class RuleCheckResult(JSONSerializable):
    def __init__(self, definition=None, state=None, error_message=None, error_traceback=None):
        self.definition = definition
        self.state = state
        self.error_message = error_message or ''
        self.error_traceback = error_traceback or ''

    @property
    def passed(self):
        return self.state == settings.CHECK_STATE_PASSED

    @property
    def failed(self):
        return self.state == settings.CHECK_STATE_FAILED

    @property
    def error(self):
        return self.state == settings.CHECK_STATE_ERROR

    def as_dict(self):
        data = {
            'rule': self.definition,
            'state': self.state,
        }
        if self.error:
            data.update({
                'error': {
                    'message': self.error_message,
                    'traceback': self.error_traceback,
                }
            })
        return data


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


class ActionRunResult(JSONSerializable):
    def __init__(self, definition=None, trigger=None, error_message=None, error_traceback=None):
        self.definition = definition
        self.trigger = trigger
        self.error_message = error_message or ''
        self.error_traceback = error_traceback or ''

    @property
    def processed(self):
        return self.state == settings.ACTION_STATE_PROCESSED

    @property
    def skipped(self):
        return self.state == settings.ACTION_STATE_SKIPPED

    @property
    def error(self):
        return self.state == settings.ACTION_STATE_ERROR

    def as_dict(self):
        data = {
            'action': self.definition,
            'state': self.state,
        }
        if self.error:
            data.update({
                'error': {
                    'message': self.error_message,
                    'traceback': self.error_traceback,
                }
            })
        return data


class ActionDefinition(JSONSerializable):
    def __init__(self, action, name=None, trigger=None):
        self.action = self._get_action(action)
        self.name = self._get_name(name)
        self.trigger = self._get_trigger(trigger)

    def _get_action(self, action):
        if not isinstance(action, Action):
            raise InvalidActionDefinition('Wrong action, actions must subclass Action')
        return action

    def _get_name(self, name):
        return name or self.action.name

    def _get_trigger(self, trigger):
        if trigger and trigger not in settings.CHECK_STATES:
            raise InvalidState("Invalid state '%s'" % trigger)
        return trigger or settings.DEFAULT_CHECK_STATE

    def as_dict(self):
        data = {
            'name': self.name,
            'trigger': self.trigger,
        }
        return data


class BaseManager(object):
    def __init__(self):
        self.definitions = []

    def _add_definition(self, definition):
        self.definitions.append(definition)


class RulesManager(BaseManager):
    def __init__(self, rules=None):
        super(RulesManager, self).__init__()
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


class ActionsManager(BaseManager):
    def __init__(self, actions=None):
        super(ActionsManager, self).__init__()
        for action in actions or []:
            self.add_action(action)

    @property
    def passed_actions(self):
        return self._get_actions_for_trigger(settings.CHECK_STATE_PASSED)

    @property
    def failed_actions(self):
        return self._get_actions_for_trigger(settings.CHECK_STATE_FAILED)

    @property
    def error_actions(self):
        return self._get_actions_for_trigger(settings.CHECK_STATE_ERROR)

    @property
    def always_actions(self):
        return self._get_actions_for_trigger(settings.CHECK_STATE_ALWAYS)

    @property
    def n_passed_actions(self):
        return len(self.passed_actions)

    @property
    def n_failed_actions(self):
        return len(self.failed_actions)

    @property
    def n_error_actions(self):
        return len(self.error_actions)

    def add_action(self, action, name=None, state=None):
        if isinstance(action, tuple):
            self._add_action_from_tuple(action)
        else:
            definition = ActionDefinition(action, name, state)
            self._add_definition(definition)

    def run_actions(self, result):
        actions_results = []
        actions_results += self._process_actions(
            actions=self.passed_actions,
            result=result,
            run_condition=result.n_passed_checks,
        )
        actions_results += self._process_actions(
            actions=self.failed_actions,
            result=result,
            run_condition=result.n_failed_checks,
        )
        actions_results += self._process_actions(
            actions=self.error_actions,
            result=result,
            run_condition=result.n_error_checks,
        )
        actions_results += self._run_actions(
            actions=self.always_actions,
            result=result,
        )
        return actions_results

    def _process_actions(self, actions, result, run_condition):
        if run_condition:
            return self._run_actions(actions, result)
        else:
            return self._skip_actions(actions)

    def _run_actions(self, actions, result):
        return [self._run_action(d, result) for d in actions]

    def _skip_actions(self, actions):
        return [self._skip_action(d) for d in actions]

    def _run_action(self, definition, result):
        action_result = ActionRunResult(definition=definition)
        try:
            definition.action.run(result)
            action_result.state = settings.ACTION_STATE_PROCESSED
        except Exception, e:
            action_result.state = settings.ACTION_STATE_ERROR
            action_result.error_message = str(e)
            action_result.error_traceback = traceback.format_exc()
        return action_result

    def _skip_action(self, definition):
        action_result = ActionRunResult(definition=definition)
        action_result.state = settings.ACTION_STATE_SKIPPED
        return action_result

    def _add_action_from_tuple(self, tuple_definition):
        state = None
        if len(tuple_definition) == 2:
            name, action = tuple_definition
        elif len(tuple_definition) == 3:
            name, action, state = tuple_definition
        else:
            raise InvalidActionDefinition('Wrong Action tuple definition, you should '
                                          'either use (name, action) or '
                                          '(name, action, state)')
        self.add_action(action=action, name=name, state=state)

    def _get_actions_for_trigger(self, state):
        return [d for d in self.definitions if d.trigger == state]
