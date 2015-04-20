import collections

from .exceptions import InvalidOperation


class Stats(collections.MutableMapping):
    """
    Immutable stats dict class that allows key access as attributes.
    ie:
    >> stats = Stats({'scraped_items': 100})
    >> stats['scraped_items']
    100
    >> stats.scraped_items
    100
    """

    def __init__(self, *args, **kwargs):
        self.__dict__['_store'] = dict(*args, **kwargs)

    def __getitem__(self, key):
        return self._store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        raise InvalidOperation("Immutable Stats! You cannot add or modify read-only stats.")

    def __delitem__(self, key):
        raise InvalidOperation("Immutable Stats! You cannot delete read-only stats.")

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

    def __setattr__(self, name, value):
        raise InvalidOperation("Immutable Stats! You cannot add or modify read-only stats.")
