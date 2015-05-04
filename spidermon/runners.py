import sys

from core.suites import MonitorSuite
from spidermon.results.monitor import MonitorResult
from spidermon.results.text import TextMonitorResult


class MonitorRunner(object):
    def __init__(self):
        self.suite = None
        self.result = None

    def run(self, suite, data=None):
        if not isinstance(suite, MonitorSuite):
            raise Exception('Not valid')  # TODO: Add custom exception
        self.suite = suite
        self.suite.init_data(**(data or {}))
        self.result = self.create_result()
        if not isinstance(self.result, MonitorResult):
            raise Exception('Not valid')  # TODO: Add custom exception
        return self.run_suite()

    def run_suite(self):
        self.result.start()
        self.run_tests()
        self.run_actions()
        self.result.finish()
        return self.result

    def run_tests(self):
        self.result.next_step()
        self.suite(self.result)
        self.result.finish_step()

    def run_actions(self):
        self.result.next_step()
        self.run_test_finish()
        self.result.finish_step()

        self.result.next_step()
        self.run_test_passsed()
        self.result.finish_step()

        self.result.next_step()
        self.run_test_fail_actions()
        self.result.finish_step()

    def run_test_finish(self):
        self.suite.on_tests_finished(self.result, self.result.all_tests)
        for action in self.suite.test_finish_actions:
            action.run(self.result)

    def run_test_passsed(self):
        self.suite.on_tests_passed(self.result, self.result.passed_tests)
        for action in self.suite.test_pass_actions:
            action.run(self.result)

    def run_test_fail_actions(self):
        self.suite.on_tests_failed(self.result, self.result.failed_tests)
        for action in self.suite.test_fail_actions:
            action.run(self.result)

    def create_result(self):
        return MonitorResult()


class TextMonitorRunner(MonitorRunner):
    def __init__(self, stream=sys.stderr, verbosity=1):
        super(TextMonitorRunner, self).__init__()
        self.stream = stream
        self.verbosity = verbosity

    def create_result(self):
        return TextMonitorResult(stream=self.stream, verbosity=self.verbosity)
