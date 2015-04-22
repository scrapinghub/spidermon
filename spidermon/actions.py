class Action(object):
    @property
    def name(self):
        return self.__class__.__name__

    def run(self, result):
        raise NotImplementedError
