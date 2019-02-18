from __future__ import absolute_import
import abc
import traceback

from spidermon.exceptions import SkipAction

from .options import ActionOptionsMetaclass
import six


class Action(six.with_metaclass(ActionOptionsMetaclass, object)):
    """
    Base class for actions.
    """

    def __init__(self):
        self.result = None
        self.data = None

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
        return "<ACTION:(%s) at %s>" % (self.name, hex(id(self)))

    def __str__(self):
        return repr(self)


class DummyAction(Action):
    def run_action(self):
        pass
