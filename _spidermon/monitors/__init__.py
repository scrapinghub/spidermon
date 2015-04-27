from spidermon.rules.managers import RulesManager
from spidermon.actions.managers import ActionsManager
from spidermon.debug import MonitorReport

from .results import MonitorResult


class Monitor(object):
    def __init__(self, name=None, rules=None, actions=None):
        self.name = name or '?'

        self.rules_manager = RulesManager(rules)
        self.add_rule = self.rules_manager.add_rule

        self.actions_manager = ActionsManager(actions)
        self.add_action = self.actions_manager.add_action

    def run(self, stats):
        result = MonitorResult(self)
        result.checks = self.rules_manager.check_rules(stats)
        result.actions = self.actions_manager.run_actions(result)
        result.stats = stats
        return result

    def debug(self):
        report = MonitorReport(self)
        return report.render()
