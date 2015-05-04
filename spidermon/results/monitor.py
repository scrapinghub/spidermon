from collections import OrderedDict
import unittest

from spidermon import settings

from .steps import TestsStep, ActionsStep


def step_required_decorator(allowed_steps):
    def _step_required_decorator(fn):
        def decorator(self, *args, **kwargs):
            if self.step.name not in allowed_steps:
                raise ValueError  # TO-DO
            else:
                return fn(self, *args, **kwargs)
        return decorator
    return _step_required_decorator

tests_step_required = step_required_decorator(settings.TESTS_STEPS)
actions_step_required = step_required_decorator(settings.ACTIONS_STEPS)


class MonitorResult(unittest.TestResult):

    def __init__(self):
        super(MonitorResult, self).__init__()
        self._steps = OrderedDict([(step, self._get_step_class(step)(step))
                                   for step in settings.STEPS])
        self._current_step = None

    @property
    def step(self):
        return self._current_step

    def start(self):
        pass

    def finish(self):
        pass

    def next_step(self):
        index = 0 if not self.step else self._steps.keys().index(self.step.name)+1
        self._current_step = self._steps.items()[index][1]
        self.step.start()

    def finish_step(self):
        self.step.finish()

    @tests_step_required
    def startTest(self, test):
        super(MonitorResult, self).startTest(test)
        self.step.add_item(test)

    @tests_step_required
    def addSuccess(self, test):
        super(MonitorResult, self).addSuccess(test)
        self.step[test].status = settings.TEST_STATUS_SUCCESS

    @tests_step_required
    def addError(self, test, error):
        super(MonitorResult, self).addError(test, error)
        self.step[test].status = settings.TEST_STATUS_ERROR
        self.step[test].error = self._exc_info_to_string(error, test)

    @tests_step_required
    def addFailure(self, test, error):
        super(MonitorResult, self).addFailure(test, error)
        self.step[test].status = settings.TEST_STATUS_FAILURE
        self.step[test].error = self._exc_info_to_string(error, test)

    @tests_step_required
    def addSkip(self, test, reason):
        super(MonitorResult, self).addSkip(test, reason)
        self.step[test].status = settings.TEST_STATUS_FAILURE
        self.step[test].reason = reason

    @tests_step_required
    def addExpectedFailure(self, test, error):
        super(MonitorResult, self).addExpectedFailure(test, error)
        self.step[test].status = settings.TEST_STATUS_EXPECTED_FAILURE
        self.step[test].error = self._exc_info_to_string(error, test)

    @tests_step_required
    def addUnexpectedSuccess(self, test):
        super(MonitorResult, self).addUnexpectedSuccess(test)
        self.step[test].status = settings.TEST_STATUS_UNEXPECTED_SUCCESS

    @actions_step_required
    def start_action(self, action):
        self.step.add_item(action)

    @actions_step_required
    def add_action_success(self, action):
        self.step[action].status = settings.ACTION_STATUS_SUCCESS

    @actions_step_required
    def add_action_skip(self, action, reason):
        self.step[action].status = settings.ACTION_STATUS_SKIPPED
        self.step[action].reason = reason

    @actions_step_required
    def add_action_error(self, action, error):
        self.step[action].status = settings.ACTION_STATUS_ERROR
        self.step[action].error = error

    @property
    def all_tests(self):
        return self._steps[settings.STEP_TESTS].all_items

    @property
    def passed_tests(self):
        return self._steps[settings.STEP_TESTS].items_for_status(settings.TEST_STATUS_SUCCESS)

    @property
    def failed_tests(self):
        return self._steps[settings.STEP_TESTS].items_for_status(settings.TEST_STATUS_FAILURE)

    def _get_step_class(self, step):
        return TestsStep if step in settings.TESTS_STEPS else ActionsStep



