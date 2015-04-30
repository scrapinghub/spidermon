from core.options import MonitorOptions
from . import settings


def _set_name_decorator(name):
    def decorator(fn):
        MonitorOptions.add_or_create(fn)
        fn.options.name = name
        return fn
    return decorator


def _set_description_decorator(description):
    def decorator(fn):
        MonitorOptions.add_or_create(fn)
        fn.options.description = description
        return fn
    return decorator


def _set_level_decorator(level):
    def decorator(fn):
        MonitorOptions.add_or_create(fn)
        fn.options.level = level
        return fn
    return decorator


def _set_order_decorator(order):
    def decorator(fn):
        MonitorOptions.add_or_create(fn)
        fn.options.order = order
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
description = _set_description_decorator
order = _set_order_decorator
