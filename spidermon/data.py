from .exceptions import InvalidDataOperation


class Data(dict):
    """
    Immutable dict class with attribute access.

    example:
    >> s = Data({'scraped_items': 100})
    >> s['scraped_items']
    100
    >> s.scraped_items
    100
    """

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("Key '%s' not found." % name)

    def _immutable(self, *args, **kws):
        raise InvalidDataOperation(
            "Immutable Data! You cannot add or modify read-only data."
        )

    update = _immutable
    setdefault = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    __setitem__ = _immutable
    __delitem__ = _immutable
    __setattr__ = _immutable
