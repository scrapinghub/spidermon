import collections
from collections.abc import Iterator
from typing import Any, NoReturn


class PercentCounterBase:
    def __init__(self, total: int = 0) -> None:
        self._total = total

    @property
    def count(self) -> int:
        raise NotImplementedError

    @property
    def percent(self) -> float:
        if self._total <= 0 or self.count <= 0:
            return 0
        return float(self.count) / float(self._total)

    def __str__(self) -> str:
        return f"(count={self.count:d}, percent={self.percent:.2f})"

    def __repr__(self) -> str:
        return self.__str__()


class PercentCounter(PercentCounterBase):
    def __init__(self, count: int = 0, total: int = 0) -> None:
        super().__init__(total)
        self._count = count

    @property
    def count(self) -> int:
        return self._count

    def inc_value(self, value: int) -> None:
        self._count += value


class DictPercentCounter(PercentCounterBase, collections.abc.MutableMapping[str, Any]):
    __items_class__: type[PercentCounterBase] = PercentCounter

    def __init__(self, total: int) -> None:
        super().__init__(total)
        self._dict: dict[str, Any] = {}

    @property
    def count(self) -> int:
        return sum([e.count for e in self._dict.values()])

    def add_value(self, key: str, value: int) -> None:
        if key not in self._dict:
            self._create_item(key)
        self[key].inc_value(value)

    def _create_item(self, key: str) -> None:
        self._dict[key] = self.__items_class__(total=self._total)

    def __getitem__(self, key: str) -> Any:
        if key not in self._dict:
            return self.__items_class__(total=self._total)
        return self._dict[self.__keytransform__(key)]

    def __iter__(self) -> Iterator[str]:
        return iter(self._dict)

    def __len__(self) -> int:
        return len(self._dict)

    def __keytransform__(self, key: str) -> str:
        return key

    def _immutable(self, *args: Any, **kws: Any) -> NoReturn:
        raise TypeError

    def __str__(self) -> str:
        return f"(count={self.count:d}, percent={self.percent:.2f}, {self._dict!s})"

    __setitem__ = _immutable
    __delitem__ = _immutable


class AttributeDictPercentCounter(PercentCounterBase):
    __attribute_dict_name__ = "dict"

    def __init__(self, total: int) -> None:
        super().__init__(total)
        setattr(self, self.__attribute_dict_name__, DictPercentCounter(total))

    @property
    def attribute_dict(self) -> DictPercentCounter:
        counter: DictPercentCounter = getattr(self, self.__attribute_dict_name__)
        return counter

    @property
    def count(self) -> int:
        return sum([e.count for e in self.attribute_dict.values()])

    def add_value(self, key: str, value: int) -> None:
        self.attribute_dict.add_value(key, value)

    def __str__(self) -> str:
        return (
            f"(count={self.count:d}, percent={self.percent:.2f}, "
            f"{self.__attribute_dict_name__}={self.attribute_dict!s})"
        )

    def __repr__(self) -> str:
        return self.__str__()
