import sys
from collections import OrderedDict
from unittest import TestResult

from . import settings


class MonitorResult(TestResult):
    def __init__(self):
        super(MonitorResult, self).__init__()
        self.test_results = OrderedDict()
        self.action_results = OrderedDict()

    def startTest(self, test):
        super(MonitorResult, self).startTest(test)
        self.test_results[test] = '?'

    def addSuccess(self, test):
        super(MonitorResult, self).addSuccess(test)
        self.test_results[test] = settings.TEST_STATUS_SUCCESS

    def addError(self, test, err):
        super(MonitorResult, self).addError(test, err)
        self.test_results[test] = settings.TEST_STATUS_ERROR

    def addFailure(self, test, err):
        super(MonitorResult, self).addFailure(test, err)
        self.test_results[test] = settings.TEST_STATUS_FAILURE

    def addSkip(self, test, reason):
        super(MonitorResult, self).addSkip(test, reason)
        self.test_results[test] = settings.TEST_STATUS_FAILURE

    def addExpectedFailure(self, test, err):
        super(MonitorResult, self).addExpectedFailure(test, err)
        self.test_results[test] = settings.TEST_STATUS_EXPECTED_FAILURE

    def addUnexpectedSuccess(self, test):
        super(MonitorResult, self).addUnexpectedSuccess(test)
        self.test_results[test] = settings.TEST_STATUS_UNEXPECTED_SUCCESS

    def start_action(self, action):
        self.action_results[action] = '?'

    def add_action_success(self, action):
        self.action_results[action] = settings.ACTION_STATUS_SUCCESS

    def add_action_skip(self, action, reason):
        self.action_results[action] = settings.ACTION_STATUS_SKIPPED

    def add_action_error(self, action, err):
        self.action_results[action] = settings.ACTION_STATUS_ERROR

    def start_run(self):
        pass

    def finish_run(self, time_taken):
        pass

    def start_tests(self):
        pass

    def finish_tests(self, time_taken):
        pass

    def start_actions(self):
        pass

    def finish_actions(self, time_taken):
        pass


class TextMonitorResult(MonitorResult):

    separator_bold = '=' * 70
    separator_light = '-' * 70

    def __init__(self, stream=sys.stderr, verbosity=1):
        super(TextMonitorResult, self).__init__()
        self.stream = stream
        self.show_all = verbosity > 1
        self.use_dots = verbosity == 1

    def _get_test_name(self, test):
        return str(test.name)

    def _get_action_name(self, action):
        return str(action.name)

    def _title_line(self, title, length=70, char=None):
        title_length = len(title)+2
        left_length = (length-title_length)/2
        right_length = left_length + length - title_length - left_length * 2
        char = char or '-'
        return '%s %s %s' % (char*left_length, title, char*right_length)

    def write_ln(self, text=None):
        self.stream.write('%s\n' % (text or ''))

    def write_status(self, text, extra=None):
        text = text
        if extra:
            text += ' (%s)' % extra
        self.write_ln(text)

    def startTest(self, test):
        super(MonitorResult, self).startTest(test)
        if self.show_all:
            self.stream.write(self._get_test_name(test))
            self.stream.write(" ... ")
            self.stream.flush()

    def addSuccess(self, test):
        super(TextMonitorResult, self).addSuccess(test)
        if self.show_all:
            self.write_status(settings.TEST_STATUS_SUCCESS)
        elif self.use_dots:
            self.stream.write('.')
            self.stream.flush()

    def addError(self, test, err):
        super(TextMonitorResult, self).addError(test, err)
        if self.show_all:
            self.write_status(settings.TEST_STATUS_ERROR)
        elif self.use_dots:
            self.stream.write('E')
            self.stream.flush()

    def addFailure(self, test, err):
        super(TextMonitorResult, self).addFailure(test, err)
        if self.show_all:
            self.write_status(settings.TEST_STATUS_FAILURE)
        elif self.use_dots:
            self.stream.write('F')
            self.stream.flush()

    def addSkip(self, test, reason):
        super(TextMonitorResult, self).addSkip(test, reason)
        if self.show_all:
            self.write_status(settings.TEST_STATUS_SKIPPED, reason)
        elif self.use_dots:
            self.stream.write("s")
            self.stream.flush()

    def addExpectedFailure(self, test, err):
        super(TextMonitorResult, self).addExpectedFailure(test, err)
        if self.show_all:
            self.write_status(settings.TEST_STATUS_EXPECTED_FAILURE)
        elif self.use_dots:
            self.stream.write("x")
            self.stream.flush()

    def addUnexpectedSuccess(self, test):
        super(TextMonitorResult, self).addUnexpectedSuccess(test)
        if self.show_all:
            self.write_status(settings.TEST_STATUS_UNEXPECTED_SUCCESS)
        elif self.use_dots:
            self.stream.write("u")
            self.stream.flush()

    def start_tests(self):
        self.write_ln(self._title_line('TESTS'))

    def finish_tests(self, time_taken):
        super(TextMonitorResult, self).finish_run(time_taken)
        if self.use_dots:
            self.write_ln()
        self._print_tests_errors()
        self._print_items_summary(time_taken, self.testsRun, 'test')
        self._print_tests_infos()

    def start_action(self, action):
        super(TextMonitorResult, self).start_action(action)
        if self.show_all:
            self.stream.write(self._get_action_name(action))
            self.stream.write(" ... ")
            self.stream.flush()

    def add_action_success(self, action):
        super(TextMonitorResult, self).add_action_success(action)
        if self.show_all:
            self.write_status(settings.ACTION_STATUS_SUCCESS)
        elif self.use_dots:
            self.stream.write('E')
            self.stream.flush()

    def add_action_skip(self, action, reason):
        super(TextMonitorResult, self).add_action_skip(action, reason)
        if self.show_all:
            self.write_status(settings.ACTION_STATUS_SKIPPED, reason)
        elif self.use_dots:
            self.stream.write('s')
            self.stream.flush()

    def add_action_error(self, action, err):
        super(TextMonitorResult, self).add_action_error(action, err)
        if self.show_all:
            self.write_status(settings.ACTION_STATUS_ERROR)
        elif self.use_dots:
            self.stream.write('.')
            self.stream.flush()

    def start_actions(self):
        self.write_ln()
        self.write_ln(self._title_line('FINISH ACTIONS'))

    def finish_actions(self, time_taken):
        if self.use_dots:
            self.write_ln()
        self._print_items_summary(time_taken, len(self.action_results), 'action')
        self._print_actions_infos()

    def _print_tests_errors(self):
        self._print_tests_error_list('ERROR', self.errors)
        self._print_tests_error_list('FAIL', self.failures)

    def _print_tests_error_list(self, flavour, errors):
        for test, err in errors:
            self.write_ln(self.separator_bold)
            self.write_ln("%s: %s" % (flavour, self._get_test_name(test)))
            self.write_ln(self.separator_light)
            self.write_ln("%s" % err)

    def _print_tests_summary(self, time_taken):
        self.write_ln(self.separator_light)
        self.write_ln("Ran %d test%s in %.3fs" %
                      (self.testsRun,
                       self.testsRun != 1 and "s" or "",
                       time_taken))
        self.write_ln()

    def _print_tests_infos(self):
        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (self.expectedFailures,
                                self.unexpectedSuccesses,
                                self.skipped))
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        if not self.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = map(len, (self.failures, self.errors))
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.write_ln(" (%s)" % (", ".join(infos),))
        else:
            self.write_ln()

    def _print_items_summary(self, time_taken, count, item_name):
        self.write_ln(self.separator_light)
        self.write_ln("Ran %d %s%s in %.3fs" %
                      (count,
                       item_name,
                       count != 1 and "s" or "",
                       time_taken))
        self.write_ln()

    def _print_actions_infos(self):
        n_skips = len([x for x in self.action_results.values()
                       if x == settings.ACTION_STATUS_SKIPPED])
        n_errors = len([x for x in self.action_results.values()
                        if x == settings.ACTION_STATUS_ERROR])
        infos = []
        if n_errors:
            self.stream.write("FAILED")
            infos.append("errors=%d" % n_errors)
        else:
            self.stream.write("OK")
        if n_skips:
            infos.append("skipped=%d" % n_skips)
        if infos:
            self.write_ln(" (%s)" % (", ".join(infos),))
        else:
            self.write_ln()