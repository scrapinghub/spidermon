import abc
import traceback

from spidermon.exceptions import SkipAction

from .options import ActionOptionsMetaclass


class Action(metaclass=ActionOptionsMetaclass):
    """
    Base class for actions.
    """

    fallback = None

    def __init__(self):
        self.result = None
        self.data = None
        if self.fallback is not None:
            self.fallback = self.fallback()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(**cls.from_crawler_kwargs(crawler))

    @classmethod
    def from_crawler_kwargs(cls, crawler):
        return {}

    @property
    def name(self):
        return self.options.name or self.__class__.__name__

    def run(self, result, data):
        self.result = result
        self.data = data
        result.start_action(self)
        try:
            self.run_action()
        except SkipAction as e:
            result.add_action_skip(self, e.args[0])
        except:
            result.add_action_error(self, traceback.format_exc())
            if self.fallback is not None:
                self.fallback.run(self.result, self.data)
        else:
            result.add_action_success(self)
        data.meta.update(self.get_meta())

    @abc.abstractmethod
    def run_action(self):
        raise NotImplementedError

    @property
    def monitors_passed(self):
        return len(self.result.monitors_passed_results) > 0

    @property
    def monitors_failed(self):
        return len(self.result.monitors_failed_results) > 0

    def get_meta(self):
        return {}

    def __repr__(self):
        return "<ACTION:({}) at {}>".format(self.name, hex(id(self)))

    def __str__(self):
        return repr(self)


class DummyAction(Action):
    def run_action(self):
        pass
