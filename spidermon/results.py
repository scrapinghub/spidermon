import sys
from collections import OrderedDict
from unittest import TestResult

from . import settings


class MonitorResult(TestResult):
    def __init__(self):
        super(MonitorResult, self).__init__()
        self._results = OrderedDict()

    def startTest(self, test):
        super(MonitorResult, self).startTest(test)
        self._results[test] = '?'

    def addSuccess(self, test):
        self._results[test] = settings.TEST_STATUS_SUCCESS
        super(MonitorResult, self).addSuccess(test)

    def addError(self, test, err):
        self._results[test] = settings.TEST_STATUS_ERROR
        super(MonitorResult, self).addError(test, err)

    def addFailure(self, test, err):
        self._results[test] = settings.TEST_STATUS_FAILURE
        super(MonitorResult, self).addFailure(test, err)

    def addSkip(self, test, reason):
        self._results[test] = settings.TEST_STATUS_FAILURE
        super(MonitorResult, self).addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self._results[test] = settings.TEST_STATUS_EXPECTED_FAILURE
        super(MonitorResult, self).addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self._results[test] = settings.TEST_STATUS_UNEXPECTED_SUCCESS
        super(MonitorResult, self).addUnexpectedSuccess(test)

    def start_run(self):
        pass

    def finish_run(self, time_taken):
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

    def finish_run(self, time_taken):
        super(TextMonitorResult, self).finish_run(time_taken)
        self._print_errors()
        self._print_summary(time_taken)
        self._print_infos()

    def _print_errors(self):
        if self.use_dots or self.show_all:
            self.write_ln()
        self._print_error_list('ERROR', self.errors)
        self._print_error_list('FAIL', self.failures)

    def _print_error_list(self, flavour, errors):
        for test, err in errors:
            self.write_ln(self.separator_bold)
            self.write_ln("%s: %s" % (flavour, self._get_test_name(test)))
            self.write_ln(self.separator_light)
            self.write_ln("%s" % err)

    def _print_summary(self, time_taken):
        self.write_ln(self.separator_light)
        self.write_ln("Ran %d test%s in %.3fs" %
                      (self.testsRun,
                       self.testsRun != 1 and "s" or "",
                       time_taken))
        self.write_ln()

    def _print_infos(self):
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
