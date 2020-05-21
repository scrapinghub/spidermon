from __future__ import absolute_import
from collections import OrderedDict
import unittest

from spidermon import settings

from .steps import MonitorStep, ActionsStep


def step_required_decorator(allowed_steps):
    def _step_required_decorator(fn):
        def decorator(self, *args, **kwargs):
            if self.step.name not in allowed_steps:
                raise ValueError  # TO-DO
            else:
                return fn(self, *args, **kwargs)

        return decorator

    return _step_required_decorator


monitors_step_required = step_required_decorator(settings.STEPS.MONITOR_RELATED)
actions_step_required = step_required_decorator(settings.STEPS.ACTION_RELATED)


class MonitorResult(unittest.TestResult):
    def __init__(self):
        super(MonitorResult, self).__init__()
        self._steps = OrderedDict(
            [(step, self._get_step_class(step)(step)) for step in settings.STEPS.ALL]
        )
        self._current_step = None

    @property
    def all_monitors_passed(self):
        return self._step_monitors.successful

    @property
    def monitor_results(self):
        return self._step_monitors.all_items

    @property
    def monitors_passed_results(self):
        return self._step_monitors.items_for_statuses(
            settings.MONITOR.STATUSES.SUCCESSFUL
        )

    @property
    def monitors_failed_results(self):
        return self._step_monitors.items_for_statuses(settings.MONITOR.STATUSES.ERROR)

    @property
    def monitors_finished_action_results(self):
        return self._step_monitors_finished.all_items

    @property
    def monitors_passed_action_results(self):
        return self._step_monitors_passed.all_items

    @property
    def monitors_failed_action_results(self):
        return self._step_monitors_failed.all_items

    @property
    def step(self):
        return self._current_step

    def start(self):
        pass

    def finish(self):
        pass

    def next_step(self):
        index = (
            0 if not self.step else list(self._steps.keys()).index(self.step.name) + 1
        )
        self._current_step = list(self._steps.items())[index][1]
        self.step.start()

    def finish_step(self):
        self.step.finish()

    @monitors_step_required
    def startTest(self, test):
        super(MonitorResult, self).startTest(test)
        self.step.add_item(test)

    @monitors_step_required
    def addSuccess(self, test):
        super(MonitorResult, self).addSuccess(test)
        self.step[test].status = settings.MONITOR.STATUS.SUCCESS

    @monitors_step_required
    def addError(self, test, error):
        super(MonitorResult, self).addError(test, error)
        self.step[test].status = settings.MONITOR.STATUS.ERROR
        self.step[test].error = self._exc_info_to_string(error, test)

    @monitors_step_required
    def addFailure(self, test, error):
        super(MonitorResult, self).addFailure(test, error)
        self.step[test].status = settings.MONITOR.STATUS.FAILURE
        self.step[test].error = self._exc_info_to_string(error, test)
        self.step[test].reason = str(error[1])

    @monitors_step_required
    def addSkip(self, test, reason):
        super(MonitorResult, self).addSkip(test, reason)
        self.step[test].status = settings.MONITOR.STATUS.FAILURE
        self.step[test].reason = reason

    @monitors_step_required
    def addExpectedFailure(self, test, error):
        super(MonitorResult, self).addExpectedFailure(test, error)
        self.step[test].status = settings.MONITOR.STATUS.EXPECTED_FAILURE
        self.step[test].error = self._exc_info_to_string(error, test)

    @monitors_step_required
    def addUnexpectedSuccess(self, test):
        super(MonitorResult, self).addUnexpectedSuccess(test)
        self.step[test].status = settings.MONITOR.STATUS.UNEXPECTED_SUCCESS

    @actions_step_required
    def start_action(self, action):
        self.step.add_item(action)

    @actions_step_required
    def add_action_success(self, action):
        self.step[action].status = settings.ACTION.STATUS.SUCCESS
        pass

    @actions_step_required
    def add_action_skip(self, action, reason):
        self.step[action].status = settings.ACTION.STATUS.SKIPPED
        self.step[action].reason = reason

    @actions_step_required
    def add_action_error(self, action, error):
        self.step[action].status = settings.ACTION.STATUS.ERROR
        self.step[action].error = error

    @actions_step_required
    def skip_all_step_actions(self, actions, reason):
        for action in actions:
            result = self.step.add_item(action)
            result.status = settings.ACTION.STATUS.SKIPPED
            result.reason = reason

    @property
    def _step_monitors(self):
        return self._steps[settings.STEPS.MONITORS]

    @property
    def _step_monitors_finished(self):
        return self._steps[settings.STEPS.MONITORS_FINISHED]

    @property
    def _step_monitors_passed(self):
        return self._steps[settings.STEPS.MONITORS_PASSED]

    @property
    def _step_monitors_failed(self):
        return self._steps[settings.STEPS.MONITORS_FAILED]

    def _get_step_class(self, step):
        return MonitorStep if step in settings.STEPS.MONITOR_RELATED else ActionsStep
