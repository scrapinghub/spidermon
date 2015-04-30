import sys
import time

from core.suites import MonitorSuite
from .results import MonitorResult, TextMonitorResult
from .exceptions import SkipAction


class MonitorRunner(object):
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
        start_time = time.time()
        self.result.start_run()
        self.run_tests()
        self.run_actions()
        self.result.finish_run(time_taken=time.time() - start_time)
        return self.result

    def run_tests(self):
        start_time = time.time()
        self.result.start_tests()
        self.suite(self.result)
        self.result.finish_tests(time_taken=time.time() - start_time)

    def run_actions(self):
        start_time = time.time()
        self.result.start_actions()
        self.run_test_finish_actions()
        self.result.finish_actions(time_taken=time.time() - start_time)

    def run_test_finish_actions(self):
        for action in self.suite.test_finish_actions:
            action.run(self.result)

    def create_result(self):
        return MonitorResult()


class TextMonitorRunner(MonitorRunner):
    def __init__(self, stream=sys.stderr, verbosity=1):
        self.stream = stream
        self.verbosity = verbosity

    def create_result(self):
        return TextMonitorResult(stream=self.stream, verbosity=self.verbosity)
