import abc
import traceback

from spidermon.exceptions import SkipAction

from .options import ActionOptionsMetaclass


class Action(object):
    """
    Base class for actions.
    """
    __metaclass__ = ActionOptionsMetaclass

    @property
    def name(self):
        return self.options.name or \
               self.__class__.__name__

    def run(self, result, data):
        result.start_action(self)
        try:
            self.run_action(result, data)
        except SkipAction, e:
            result.add_action_skip(self, e.message)
        except:
            result.add_action_error(self, traceback.format_exc())
        else:
            result.add_action_success(self)

    @abc.abstractmethod
    def run_action(self, result, data):
        raise NotImplementedError

    def __repr__(self):
        return '<ACTION:(%s) at %s>' % (self.name, hex(id(self)))

    def __str__(self):
        return repr(self)


class DummyAction(Action):
    def run_action(self, result, data):
        pass