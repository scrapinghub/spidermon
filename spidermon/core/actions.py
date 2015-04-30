class Action(object):
    """
    Base class for actions.
    """
    @property
    def name(self):
        return self.__class__.__name__

    def run(self, result):
        raise NotImplementedError
