import traceback

from spidermon.exceptions import InvalidActionDefinition
from spidermon import settings

from .definitions import ActionDefinition
from .results import ActionRunResult


class ActionsManager(object):
    def __init__(self, actions=None):
        self.definitions = []
        for action in actions or []:
            self.add_action(action)

    def _add_definition(self, definition):
        self.definitions.append(definition)

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