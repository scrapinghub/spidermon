from spidermon.serialization import JSONSerializable
from spidermon import settings


class ActionRunResult(JSONSerializable):
    def __init__(self, definition=None, state=None, error_message=None, error_traceback=None):
        self.definition = definition
        self.state = state
        self.error_message = error_message or ''
        self.error_traceback = error_traceback or ''

    @property
    def processed(self):
        return self.state == settings.ACTION_STATE_PROCESSED

    @property
    def skipped(self):
        return self.state == settings.ACTION_STATE_SKIPPED

    @property
    def error(self):
        return self.state == settings.ACTION_STATE_ERROR

    def as_dict(self):
        data = {
            'action': self.definition,
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
