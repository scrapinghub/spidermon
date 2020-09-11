from __future__ import absolute_import
import collections


class PercentCounterBase(object):
    def __init__(self, total=0):
        self._total = total

    @property
    def count(self):
        raise NotImplementedError

    @property
    def percent(self):
        if self._total <= 0 or self.count <= 0:
            return 0
        else:
            return float(self.count) / float(self._total)

    def __str__(self):
        return "(count=%d, percent=%.2f)" % (self.count, self.percent)

    def __repr__(self):
        return self.__str__()


class PercentCounter(PercentCounterBase):
    def __init__(self, count=0, total=0):
        super(PercentCounter, self).__init__(total)
        self._count = count

    @property
    def count(self):
        return self._count

    def inc_value(self, value):
        self._count += value


class DictPercentCounter(PercentCounterBase, collections.abc.MutableMapping):
    __items_class__ = PercentCounter

    def __init__(self, total):
        super(DictPercentCounter, self).__init__(total)
        self._dict = dict()

    @property
    def count(self):
        return sum([e.count for e in self._dict.values()])

    def add_value(self, key, value):
        if key not in self._dict:
            self._create_item(key)
        self[key].inc_value(value)

    def _create_item(self, key):
        self._dict[key] = self.__items_class__(total=self._total)

    def __getitem__(self, key):
        if key not in self._dict:
            return self.__items_class__(total=self._total)
        else:
            return self._dict[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __keytransform__(self, key):
        return key

    def _immutable(self, *args, **kws):
        raise TypeError

    def __str__(self):
        return "(count=%d, percent=%.2f, %s)" % (
            self.count,
            self.percent,
            str(self._dict),
        )

    __setitem__ = _immutable
    __delitem__ = _immutable


class AttributeDictPercentCounter(PercentCounterBase):
    __attribute_dict_name__ = "dict"

    def __init__(self, total):
        super(AttributeDictPercentCounter, self).__init__(total)
        setattr(self, self.__attribute_dict_name__, DictPercentCounter(total))

    @property
    def attribute_dict(self):
        return getattr(self, self.__attribute_dict_name__)

    @property
    def count(self):
        return sum([e.count for e in self.attribute_dict.values()])

    def add_value(self, key, value):
        self.attribute_dict.add_value(key, value)

    def __str__(self):
        return "(count=%d, percent=%.2f, %s=%s)" % (
            self.count,
            self.percent,
            self.__attribute_dict_name__,
            str(self.attribute_dict),
        )

    def __repr__(self):
        return self.__str__()
