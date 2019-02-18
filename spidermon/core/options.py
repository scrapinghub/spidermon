from __future__ import absolute_import
import abc
from spidermon import settings


class OptionsMetaclassBase(abc.ABCMeta):
    __options_class__ = None

    def __new__(mcs, name, bases, attrs):
        cls = super(OptionsMetaclassBase, mcs).__new__(mcs, name, bases, attrs)
        if not cls.__options_class__:
            raise TypeError(
                "Options class not defined! "
                "are you trying to use OptionsMetaclassBase?"
            )
        cls.options = cls.__options_class__()
        return cls


class OptionsBase(object):
    __options_name__ = "options"

    @classmethod
    def add_or_create(cls, target):
        if not hasattr(target, cls.__options_name__):
            setattr(target, cls.__options_name__, cls())
            return True
        return False

    def _get_attributes(self):
        return dict([(k, v) for k, v in self.__dict__.items() if not k.startswith("_")])

    def __str__(self):
        return "<{name}:({attributes})>".format(
            name=self.__class__.__name__,
            attributes=", ".join(
                "%s=%s" % (attr, getattr(self, attr)) for attr in self._get_attributes()
            ),
        )


class MonitorOptions(OptionsBase):
    def __init__(self):
        self.name = settings.MONITOR.DEFAULT_NAME
        self.description = settings.MONITOR.DEFAULT_DESCRIPTION
        self.level = None
        self.meta = {}
        self.order = settings.MONITOR.DEFAULT_ORDER


class MonitorOptionsMetaclass(OptionsMetaclassBase):
    __options_class__ = MonitorOptions


class ActionOptions(OptionsBase):
    def __init__(self):
        self.name = None
        self.description = settings.ACTION.DEFAULT_DESCRIPTION


class ActionOptionsMetaclass(OptionsMetaclassBase):
    __options_class__ = ActionOptions
