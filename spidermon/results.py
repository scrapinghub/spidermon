import sys
from collections import OrderedDict
import unittest
import time

from . import settings


DOTS = {
    # Tests
    settings.TEST_STATUS_SUCCESS: '.',
    settings.TEST_STATUS_ERROR: 'E',
    settings.TEST_STATUS_FAILURE: 'F',
    settings.TEST_STATUS_SKIPPED: 's',
    settings.TEST_STATUS_EXPECTED_FAILURE: 'x',
    settings.TEST_STATUS_UNEXPECTED_SUCCESS: 'u',

    # Actions
    settings.ACTION_STATUS_SUCCESS: '.',
    settings.ACTION_STATUS_ERROR: 'E',
    settings.ACTION_STATUS_SKIPPED: 's',
}


class ItemResult(object):
    def __init__(self, item):
        self.item = item
        self.status = settings.UNDEFINED_STATUS
        self.error = None
        self.reason = None


class TestResult(ItemResult):
    name = 'test'


class ActionResult(ItemResult):
    name = 'action'


class Step(object):
    item_result_class = ItemResult
    successful_statuses = []
    error_statuses = []

    def __init__(self, name):
        self.name = name
        self._results = OrderedDict()
        self.start_time = 0
        self.finish_time = 0

    @property
    def time_taken(self):
        return self.finish_time - self.start_time

    @property
    def successful(self):
        for result in self._results.values():
            if result.status not in self.successful_statuses:
                return False
        return True

    @property
    def number_of_items(self):
        return len(self._results)

    def add_item(self, item):
        self._results[item] = self.item_result_class(item)

    def start(self):
        #print 'starting step', self.name
        self.start_time = time.time()

    def finish(self):
        self.finish_time = time.time()

    def items_for_status(self, status):
        return [result for item, result in self._results.items()
                if result.status == status]

    def get_infos(self):
        raise NotImplementedError

    def __getitem__(self, key):
        return self._results[key]


class TestsStep(Step):
    item_result_class = TestResult
    successful_statuses = settings.TESTS_SUCCESSFUL_STATUSES
    error_statuses = settings.TESTS_ERROR_STATUSES

    def get_infos(self):
        return {
            'failures': len(self.items_for_status(settings.TEST_STATUS_FAILURE)),
            'errors': len(self.items_for_status(settings.TEST_STATUS_ERROR)),
            'skipped': len(self.items_for_status(settings.TEST_STATUS_SKIPPED)),
            'expected failures': len(self.items_for_status(settings.TEST_STATUS_EXPECTED_FAILURE)),
            'unexpected successes': len(self.items_for_status(settings.TEST_STATUS_UNEXPECTED_SUCCESS)),
        }


class ActionsStep(Step):
    item_result_class = ActionResult
    successful_statuses = settings.ACTIONS_SUCCESSFUL_STATUSES
    error_statuses = settings.ACTIONS_ERROR_STATUSES

    def get_infos(self):
        return {
            'errors': len(self.items_for_status(settings.ACTION_STATUS_ERROR)),
            'skipped': len(self.items_for_status(settings.ACTION_STATUS_SKIPPED)),
        }


STEP_TESTS = 'TESTS'
STEP_FINISH_ACTIONS = 'FINISH ACTIONS'
STEP_PASS_ACTIONS = 'PASS ACTIONS'
STEP_FAIL_ACTIONS = 'FAIL ACTIONS'

STEPS = [STEP_TESTS, STEP_FINISH_ACTIONS, STEP_PASS_ACTIONS, STEP_FAIL_ACTIONS]
TESTS_STEPS = [STEP_TESTS]
ACTIONS_STEPS = [STEP_FINISH_ACTIONS, STEP_PASS_ACTIONS, STEP_FAIL_ACTIONS]


def step_required_decorator(allowed_steps):
    def _step_required_decorator(fn):
        def decorator(self, *args, **kwargs):
            if self.step.name not in allowed_steps:
                raise ValueError # TO-DO
            else:
                return fn(self, *args, **kwargs)
        return decorator
    return _step_required_decorator

tests_step_required = step_required_decorator(TESTS_STEPS)
actions_step_required = step_required_decorator(ACTIONS_STEPS)


class MonitorResult(unittest.TestResult):

    def __init__(self):
        super(MonitorResult, self).__init__()
        self._steps = OrderedDict([(step, self._get_step_class(step)(step))
                                   for step in STEPS])
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


class TextMonitorResult(MonitorResult):

    SEPARATOR_BOLD = '='
    SEPARATOR_LIGHT = '-'
    LINE_LENGTH = 70

    def __init__(self, stream=sys.stderr, verbosity=1):
        super(TextMonitorResult, self).__init__()
        self.stream = stream
        self.show_all = verbosity > 1
        self.use_dots = verbosity == 1

    def next_step(self):
        super(TextMonitorResult, self).next_step()
        self.write_title(self.step.name)

    def finish_step(self):
        super(TextMonitorResult, self).finish_step()
        if self.use_dots:
            self.write_line()
        if not self.step.successful:
            self.write_errors()
        self.write_run_footer()
        self.write_step_summary()

    @tests_step_required
    def startTest(self, test):
        super(TextMonitorResult, self).startTest(test)
        self.write_run_start(test)

    @tests_step_required
    def addSuccess(self, test):
        super(TextMonitorResult, self).addSuccess(test)
        self.write_run_result(test)

    @tests_step_required
    def addError(self, test, error):
        super(TextMonitorResult, self).addError(test, error)
        self.write_run_result(test)

    @tests_step_required
    def addFailure(self, test, error):
        super(TextMonitorResult, self).addFailure(test, error)
        self.write_run_result(test)

    @tests_step_required
    def addSkip(self, test, reason):
        super(TextMonitorResult, self).addSkip(test, reason)
        self.write_run_result(test, reason)

    @tests_step_required
    def addExpectedFailure(self, test, err):
        super(TextMonitorResult, self).addExpectedFailure(test, err)
        self.write_run_result(test)

    @tests_step_required
    def addUnexpectedSuccess(self, test):
        super(TextMonitorResult, self).addUnexpectedSuccess(test)
        self.write_run_result(test)

    @actions_step_required
    def start_action(self, action):
        super(TextMonitorResult, self).start_action(action)
        self.write_run_start(action)

    @actions_step_required
    def add_action_success(self, action):
        super(TextMonitorResult, self).add_action_success(action)
        self.write_run_result(action)

    @actions_step_required
    def add_action_skip(self, action, reason):
        super(TextMonitorResult, self).add_action_skip(action, reason)
        self.write_run_result(action, reason)

    @actions_step_required
    def add_action_error(self, action, err):
        super(TextMonitorResult, self).add_action_error(action, err)
        self.write_run_result(action)

    def write(self, text):
        self.stream.write(text)

    def write_flush(self):
        self.stream.flush()

    def write_line_light(self):
        self.write_line(self.SEPARATOR_LIGHT*self.LINE_LENGTH)

    def write_line_bold(self):
        self.write_line(self.SEPARATOR_BOLD*self.LINE_LENGTH)

    def write_title(self, title):
        self.write_line(self._line_title(title))

    def write_line(self, text=None):
        self.write('%s\n' % (text or ''))

    def write_run_status(self, text, extra=None):
        self.write_line('%s%s' % (text, ' (%s)' % extra if extra else ''))

    def write_run_start(self, item):
        if self.show_all:
            self.write(item.name)
            self.write(" ... ")
            self.write_flush()

    def write_run_result(self, item, extra=None):
        if self.show_all:
            self.write_run_status(self.step[item].status, extra)
        elif self.use_dots:
            self.write(DOTS[self.step.results[item]])
            self.write_flush()

    def write_run_footer(self):
        self.write_line_light()
        self.write_line("{count:d} {item_name}{plural_suffix} in {time:.3f}s".format(
            count=self.step.number_of_items,
            item_name=self.step.item_result_class.name,
            plural_suffix='' if self.step.number_of_items == 1 else 's',
            time=self.step.time_taken,
        ))
        self.write_line()

    def write_errors(self):
        self.write_line()
        for status in self.step.error_statuses:
            for item in self.step.items_for_status(status):
                self.write_line_bold()
                self.write_line('%s: %s' % (item.status, item.name))
                self.write_line_light()
                self.write_line(item.error)
                self.write_line()

    def write_step_summary(self):
        self.write('OK' if self.step.successful else 'FAILED')
        infos = self.step.get_infos()
        if infos and sum(infos.values()):
            self.write_line(' (%s)' % ', '.join(['%s=%s' % (k, v) for k, v in infos.items() if v]))
        else:
            self.write_line()
        self.write_line()

    def _line_title(self, title, length=70, char=None):
        title_length = len(title)+2
        left_length = (length-title_length)/2
        right_length = left_length + length - title_length - left_length * 2
        char = char or self.SEPARATOR_LIGHT
        return '%s %s %s' % (char*left_length, title, char*right_length)

    def _get_step_class(self, step):
        return TestsStep if step in TESTS_STEPS else ActionsStep
