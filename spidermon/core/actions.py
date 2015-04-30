from .options import ActionOptions, ActionOptionsMetaclass


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
        raise NotImplementedError
