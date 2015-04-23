from spidermon.serialization import JSONSerializable
from spidermon.exceptions import InvalidActionDefinition, InvalidState
from spidermon import settings

from . import Action


class ActionDefinition(JSONSerializable):
    def __init__(self, action, name=None, trigger=None):
        self.action = self._get_action(action)
        self.name = self._get_name(name)
        self.trigger = self._get_trigger(trigger)

    def _get_action(self, action):
        if not isinstance(action, Action):
            raise InvalidActionDefinition('Wrong action, actions must subclass Action')
        return action

    def _get_name(self, name):
        return name or self.action.name

    def _get_trigger(self, trigger):
        if trigger and trigger not in settings.ACTION_TRIGGERS:
            raise InvalidState("Invalid state '%s'" % trigger)
        return trigger or settings.DEFAULT_CHECK_STATE

    def as_dict(self):
        data = {
            'name': self.name,
            'trigger': self.trigger,
        }
        return data
