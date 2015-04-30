import collections

from .exceptions import InvalidStatsOperation


class Stats(collections.MutableMapping):
    """
    Immutable stats dict class that allows key access as attributes.

    example:
    >> s = Stats({'scraped_items': 100})
    >> s['scraped_items']
    100
    >> s.scraped_items
    100
    """

    def __init__(self, *args, **kwargs):
        self.__dict__['_store'] = dict(*args, **kwargs)

    def __getitem__(self, key):
        return self._store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def __keytransform__(self, key):
        return key

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("Stats key '%s' not found." % name)

    def __repr__(self):
        return str(dict(self))

    def _immutable(self, *args, **kws):
        raise InvalidStatsOperation('Immutable Stats! You cannot add or modify read-only stats.')

    __setitem__ = _immutable
    __delitem__ = _immutable
    __setattr__ = _immutable