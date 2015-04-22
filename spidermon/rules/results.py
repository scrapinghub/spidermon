from spidermon.serialization import JSONSerializable
from spidermon import settings


class RuleCheckResult(JSONSerializable):
    def __init__(self, definition=None, state=None, error_message=None, error_traceback=None):
        self.definition = definition
        self.state = state
        self.error_message = error_message or ''
        self.error_traceback = error_traceback or ''

    @property
    def passed(self):
        return self.state == settings.CHECK_STATE_PASSED

    @property
    def failed(self):
        return self.state == settings.CHECK_STATE_FAILED

    @property
    def error(self):
        return self.state == settings.CHECK_STATE_ERROR

    def as_dict(self):
        data = {
            'rule': self.definition,
            'state': self.state,
        }
        if self.error:
            data.update({
                'error': {
                    'message': self.error_message,
                    'traceback': self.error_traceback,
                }
            })
        return data
