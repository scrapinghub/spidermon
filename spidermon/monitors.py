from .managers import RulesManager
from .serialization import JSONSerializable
from . import settings


class MonitorResult(JSONSerializable):
    def __init__(self, monitor, checks=None):
        self.monitor = monitor
        self.checks = checks or []

    def to_json(self):
        data = {
            'monitor': self.monitor.name,
            'checks': self.checks,
            'summary': {
                'rules': {
                    'total': len(self.monitor.rules_manager.definitions),
                },
            }
        }
        data['summary']['rules'].update(self._get_check_counts())
        return data

    def _get_check_count(self, result):
        return len([c for c in self.checks if c.result == result])

    def _get_check_counts(self):
        return dict([(result, self._get_check_count(result)) for result in settings.CHECK_RESULTS])


class Monitor(object):
    def __init__(self, name=None, rules=None):
        self.name = name or '?'
        self.rules_manager = RulesManager(rules)
        self.add_rule = self.rules_manager.add_rule

    def run(self, stats):
        result = MonitorResult(self)
        result.checks = self.rules_manager.check_rules(stats)
        return result
