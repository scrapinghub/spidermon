from . import settings


class OptionsMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        cls = super(OptionsMetaclass, mcs).__new__(mcs, name, bases, attrs)
        cls.options = Options()
        return cls


class Options(object):
    options_name = 'options'
    options_attributes = ['name', 'level', 'meta']

    def __init__(self):
        self.name = None
        self.level = settings.DEFAULT_MONITOR_LEVEL
        self.meta = {}

    @classmethod
    def add_or_create(cls, target):
        if not hasattr(target, cls.options_name):
            setattr(target, cls.options_name, Options())
            return True
        return False

    def __str__(self):
        return '<Options:(%s)>' % ', '.join('%s=%s' % (attr, getattr(self, attr))
                                            for attr in self.options_attributes)
