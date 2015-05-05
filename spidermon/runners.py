import sys

from spidermon.core.suites import MonitorSuite
from spidermon.results.monitor import MonitorResult
from spidermon.results.text import TextMonitorResult
from spidermon.exceptions import InvalidMonitor, InvalidResult


class MonitorRunner(object):
    def __init__(self):
        self.suite = None
        self.result = None

    def run(self, suite, data=None):
        if not isinstance(suite, MonitorSuite):
            raise InvalidMonitor('Runners must receive a MonitorSuite instance')
        self.suite = suite
        self.suite.init_data(**(data or {}))
        self.result = self.create_result()
        if not isinstance(self.result, MonitorResult):
            raise InvalidResult('Runners must use a MonitorResult instance')
        return self.run_suite()

    def run_suite(self):
        self.result.start()
        self.run_monitors()
        self.run_actions()
        self.result.finish()
        return self.result

    def run_monitors(self):
        self.result.next_step()
        self.suite(self.result)
        self.result.finish_step()

    def run_actions(self):
        # Run monitors finished actions
        self.result.next_step()
        self.run_monitors_finished()
        self.result.finish_step()

        # Run monitors passed actions
        self.result.next_step()
        if self.result.monitor_results and self.result.all_monitors_passed:
            self.run_monitors_passsed()
        else:
            self.result.skip_all_step_actions(
                actions=self.suite.monitors_passed_actions,
                reason='A Monitor failed')
        self.result.finish_step()

        # Run monitors failed actions
        self.result.next_step()
        if self.result.monitor_results and not self.result.all_monitors_passed:
            self.run_monitors_failed()
        else:
            self.result.skip_all_step_actions(
                actions=self.suite.monitors_failed_actions,
                reason='No Monitors failed')
        self.result.finish_step()

    def run_monitors_finished(self):
        self.suite.on_monitors_finished(self.result)
        for action in self.suite.monitors_finished_actions:
            action.run(self.result)

    def run_monitors_passsed(self):
        self.suite.on_monitors_passed(self.result)
        for action in self.suite.monitors_passed_actions:
            action.run(self.result)

    def run_monitors_failed(self):
        self.suite.on_monitors_failed(self.result)
        for action in self.suite.monitors_failed_actions:
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
