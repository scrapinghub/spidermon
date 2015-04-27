from spidermon.serialization import JSONSerializable
from spidermon.debug import MonitorResultsReport
from spidermon import settings


class MonitorResult(JSONSerializable):
    def __init__(self, monitor, checks=None, actions=None, stats=None):
        self.monitor = monitor
        self.checks = checks or []
        self.actions = actions or []
        self.stats = stats or {}

    @property
    def passed_checks(self):
        return self._get_checks(settings.CHECK_STATE_PASSED)

    @property
    def failed_checks(self):
        return self._get_checks(settings.CHECK_STATE_FAILED)

    @property
    def error_checks(self):
        return self._get_checks(settings.CHECK_STATE_ERROR)

    @property
    def n_checks(self):
        return len(self.checks)

    @property
    def n_passed_checks(self):
        return len(self.passed_checks)

    @property
    def n_failed_checks(self):
        return len(self.failed_checks)

    @property
    def n_error_checks(self):
        return len(self.error_checks)

    @property
    def processed_actions(self):
        return self._get_actions(settings.ACTION_STATE_PROCESSED)

    @property
    def skipped_actions(self):
        return self._get_actions(settings.ACTION_STATE_SKIPPED)

    @property
    def error_actions(self):
        return self._get_actions(settings.ACTION_STATE_ERROR)

    @property
    def n_actions(self):
        return len(self.actions)

    @property
    def n_processed_actions(self):
        return len(self.processed_actions)

    @property
    def n_skipped_actions(self):
        return len(self.skipped_actions)

    @property
    def n_error_actions(self):
        return len(self.error_actions)

    def as_dict(self):
        data = {
            'monitor': self.monitor.name,
            'checks': self.checks,
            'actions': self.actions,
            'stats': self.stats,
            'summary': {
                'rules': {
                    'total': len(self.monitor.rules_manager.definitions),
                },
            }
        }
        data['summary']['rules'].update(self._get_check_counts())
        return data

    def debug(self):
        report = MonitorResultsReport(self)
        return report.render()

    def _get_checks(self, state):
        return [c for c in self.checks if c.state == state]

    def _get_check_count(self, state):
        return len(self._get_checks(state))

    def _get_check_counts(self):
        return dict([(state, self._get_check_count(state)) for state in settings.CHECK_STATES])

    def _get_actions(self, state):
        return [a for a in self.actions if a.state == state]
