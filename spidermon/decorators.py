from .options import Options
from . import settings


def _set_name_decorator(name):
    def decorator(fn):
        Options.add_or_create(fn)
        fn.options.name = name
        return fn
    return decorator


def _set_level_decorator(level):
    def decorator(fn):
        Options.add_or_create(fn)
        fn.options.level = level
        return fn
    return decorator


class LevelDecoratorGenerator:
    allowed_levels = [l.lower() for l in settings.MONITOR_LEVELS]

    def __getattr__(self, name):
        if name not in self.allowed_levels:
            raise AttributeError('Invalid level')
        else:
            return _set_level_decorator(name.upper())

level = LevelDecoratorGenerator()
name = _set_name_decorator
