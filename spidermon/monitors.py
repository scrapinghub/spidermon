from .managers import RulesManager
from .serialization import JSONSerializable


class MonitorResult(JSONSerializable):
    def __init__(self, monitor, rule_checks=None):
        self.monitor = monitor
        self.rule_checks = rule_checks or []

    def to_json(self):
        data = {
            'monitor': self.monitor.name,
            'rule_checks': self.rule_checks,
        }
        return data


class Monitor(object):
    def __init__(self, name=None, rules=None):
        self.name = name or '?'
        self.rules_manager = RulesManager(rules)
        self.add_rule = self.rules_manager.add_rule

    def run(self, stats):
        result = MonitorResult(self)
        result.rule_checks = self.rules_manager.check_rules(stats)
        return result
