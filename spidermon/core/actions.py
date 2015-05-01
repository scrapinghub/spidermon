import sys
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

    def run(self, result):
        result.start_action(self)
        try:
            self.run_action(result)
        except SkipAction, e:
            result.add_action_skip(self, e.message)
        except:
            result.add_action_error(self, traceback.format_exc())
        else:
            result.add_action_success(self)

    def run_action(self, result):
        raise NotImplementedError

    def __repr__(self):
        return '<ACTION:(%s) at %s>' % (self.name, hex(id(self)))

    def __str__(self):
        return repr(self)

