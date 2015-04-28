import sys
import time

from .suites import MonitorSuite
from .results import MonitorResult, TextMonitorResult


class MonitorRunner(object):
    def run(self, suite, data):
        if not isinstance(suite, MonitorSuite):
            raise Exception('Not valid')  # TODO: Add custom exception
        suite.init_data(**data)
        return self.run_suite(suite)

    def run_suite(self, suite):
        result = self.create_result()
        if not isinstance(result, MonitorResult):
            raise Exception('Not valid')  # TODO: Add custom exception
        start_time = time.time()
        result.start_run()
        suite(result)
        time_taken = time.time() - start_time
        result.finish_run(time_taken)
        return result

    def create_result(self):
        return MonitorResult()


class TextMonitorRunner(MonitorRunner):
    def __init__(self, stream=sys.stderr, verbosity=1):
        self.stream = stream
        self.verbosity = verbosity

    def create_result(self):
        return TextMonitorResult(stream=self.stream, verbosity=self.verbosity)


from unittest import TextTestRunner


class OldTextRunner(TextTestRunner):
    def run(self, suite, data):
        if not isinstance(suite, MonitorSuite):
            raise Exception('Not valid')  # TODO: Add custom exception
        suite.init_data(**data)
        return super(OldTextRunner, self).run(suite)
