from .exceptions import InvalidDataOperation


class Data(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("Key '%s' not found." % name)

    def _immutable(self, *args, **kws):
        raise InvalidDataOperation('Immutable Data! You cannot add or modify read-only data.')

    update = _immutable
    setdefault = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    __setitem__ = _immutable
    __delitem__ = _immutable
    __setattr__ = _immutable