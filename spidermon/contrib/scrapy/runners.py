import logging

from spidermon.results.monitor import (
    MonitorResult,
    actions_step_required,
    monitors_step_required,
)
from spidermon.runners import MonitorRunner
from spidermon.utils.text import Message, line, line_title

LOG_MESSAGE_HEADER = "Spidermon"


class SpiderMonitorResult(MonitorResult):
    def __init__(self, spider):
        super().__init__()
        self.spider = spider

    def next_step(self):
        super().next_step()
        self.write_title()

    def finish_step(self):
        super().finish_step()
        self.log_info(line())
        if not self.step.successful:
            self.write_errors()
        self.write_run_footer()
        self.write_step_summary()

    @monitors_step_required
    def addSuccess(self, test):
        super().addSuccess(test)
        self.write_item_result(test)

    @monitors_step_required
    def addError(self, test, error):
        super().addError(test, error)
        self.write_item_result(test)

    @monitors_step_required
    def addFailure(self, test, error):
        super().addFailure(test, error)
        self.write_item_result(test)

    @monitors_step_required
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.write_item_result(test, reason)

    @monitors_step_required
    def addExpectedFailure(self, test, error):
        super().addExpectedFailure(test, error)
        self.write_item_result(test)

    @monitors_step_required
    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.write_item_result(test)

    @actions_step_required
    def add_action_success(self, action):
        super().add_action_success(action)
        self.write_item_result(action)

    @actions_step_required
    def add_action_skip(self, action, reason):
        super().add_action_skip(action, reason)
        self.write_item_result(action, reason)

    @actions_step_required
    def add_action_error(self, action, error):
        super().add_action_error(action, error)
        self.write_item_result(action)

    def write_title(self):
        self.log_info(line_title(self.step.name))

    def write_item_result(self, item, extra=None):
        self.log_info(
            "%s... %s%s"
            % (item.name, self.step[item].status, " (%s)" % extra if extra else "")
        )

    def write_run_footer(self):
        self.log_info(
            "{count:d} {item_name}{plural_suffix} in {time:.3f}s".format(
                count=self.step.number_of_items,
                item_name=self.step.item_result_class.name,
                plural_suffix="" if self.step.number_of_items == 1 else "s",
                time=self.step.time_taken,
            )
        )

    def write_step_summary(self):
        summary = "OK" if self.step.successful else "FAILED"
        infos = self.step.get_infos()
        if infos and sum(infos.values()):
            summary += " (%s)" % ", ".join([f"{k}={v}" for k, v in infos.items() if v])
        self.log_info(summary)

    def write_errors(self):
        for status in self.step.error_statuses:
            for item in self.step.items_for_status(status):
                msg = Message()
                msg.write_line()
                msg.write_bold_separator()
                msg.write_line(f"{item.status}: {item.item.name}")
                msg.write_light_separator()
                msg.write(item.error)
                self.log_error(msg)

    def log_error(self, msg):
        self.log(msg, level=logging.ERROR)

    def log_info(self, msg):
        self.log(msg, level=logging.INFO)

    def log(self, msg, level=logging.DEBUG):
        self.spider.log(f"[{LOG_MESSAGE_HEADER}] {msg}", level=level)


class SpiderMonitorRunner(MonitorRunner):
    def __init__(self, spider):
        super().__init__()
        self.spider = spider

    def create_result(self):
        return SpiderMonitorResult(self.spider)
