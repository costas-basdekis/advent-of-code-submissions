import itertools
from typing import Iterable, Tuple, TypeVar, List, Optional, Sized, cast, Dict, \
    Callable

__all__ = [
    'KeyedDefaultDict',
    'get_fixed_length_substrings',
    'all_possible_combinations',
    'all_possible_permutations',
    'all_possible_quantity_splits',
    'get_windows',
    'iterable_length',
    'count_by',
]


class KeyedDefaultDict(dict):
    def __init__(self, default_factory, **kwargs):
        self.default_factory = default_factory
        super().__init__(kwargs)

    def __missing__(self, key):
        """
        >>> _dict = KeyedDefaultDict(lambda _key: _key)
        >>> _dict[5]
        5
        >>> _dict
        {5: 5}
        >>> _dict = KeyedDefaultDict(lambda _key: [_key])
        >>> _dict[5]
        [5]
        >>> _dict
        {5: [5]}
        >>> _dict[6] is _dict[6]
        True
        >>> _dict[7] = 10
        >>> _dict[7]
        10
        >>> _dict
        {5: [5], 6: [6], 7: 10}
        """
        value = self[key] = self.default_factory(key)
        return value


S = TypeVar('S')
T = TypeVar('T')


def get_fixed_length_substrings(text: str, length: int) -> Iterable[str]:
    """
    >>> list(get_fixed_length_substrings("", 4))
    []
    >>> list(get_fixed_length_substrings("abc", 4))
    []
    >>> list(get_fixed_length_substrings("abc", 3))
    ['abc']
    >>> list(get_fixed_length_substrings("abc", 2))
    ['ab', 'bc']
    >>> list(get_fixed_length_substrings("abcdefg", 2))
    ['ab', 'bc', 'cd', 'de', 'ef', 'fg']
    """
    return (
        text[start:start + length]
        for start in range(len(text) - length + 1)
    )


def all_possible_combinations(items: List[T]) -> Iterable[Tuple[T, ...]]:
    """
    >>> sorted(all_possible_combinations([]))
    [()]
    >>> sorted(all_possible_combinations([1]))
    [(), (1,)]
    >>> sorted(all_possible_combinations([1, 2, 3]))
    [(), (1,), (1, 2), (1, 2, 3), (1, 3), (2,), (2, 3), (3,)]
    """
    return (
        combination
        for length in range(len(items) + 1)
        for combination in itertools.combinations(items, length)
    )


def all_possible_permutations(items: List[T]) -> Iterable[Tuple[T, ...]]:
    """
    >>> sorted(all_possible_permutations([]))
    [()]
    >>> sorted(all_possible_permutations([1]))
    [(), (1,)]
    >>> sorted(all_possible_permutations([1, 2, 3]))
    [(), (1,), (1, 2), (1, 2, 3), (1, 3), (1, 3, 2), (2,), (2, 1), (2, 1, 3),
        (2, 3), (2, 3, 1), (3,), (3, 1), (3, 1, 2), (3, 2), (3, 2, 1)]
    """
    return (
        permutation
        for combination in all_possible_combinations(items)
        for permutation in itertools.permutations(combination)
    )


def all_possible_quantity_splits(total: int, count: int,
                                 ) -> Iterable[Tuple[int, ...]]:
    """
    >>> sorted(all_possible_quantity_splits(5, 1))
    [(5,)]
    >>> sorted(all_possible_quantity_splits(5, 2))
    [(0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0)]
    >>> sorted(all_possible_quantity_splits(2, 3))
    [(0, 0, 2), (0, 1, 1), (0, 2, 0), (1, 0, 1), (1, 1, 0), (2, 0, 0)]
    """
    if count < 1:
        raise Exception(f"Expected count more than, got {count}")
    if total < 0:
        raise Exception(f"Expected total more or equal to 0, got {total}")
    if total == 0:
        yield (0,) * count
        return
    if count == 1:
        yield total,
        return

    for first in range(total + 1):
        for rest in all_possible_quantity_splits(total - first, count - 1):
            yield (first,) + rest


def get_windows(items: Iterable[T], size: int) -> Iterable[Tuple[T, ...]]:
    """
    >>> list(get_windows(range(0), 3))
    []
    >>> list(get_windows(range(1), 3))
    []
    >>> list(get_windows(range(2), 3))
    []
    >>> list(get_windows(range(3), 3))
    [(0, 1, 2)]
    >>> list(get_windows(range(6), 3))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5)]
    >>> list(get_windows(range(7), 3))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6)]
    """
    next_window = tuple()
    for item in items:
        next_window += (item,)
        if len(next_window) >= size:
            next_window = next_window[-size:]
            yield next_window


def last(items: Iterable[T], default: T = NotImplemented) -> Optional[T]:
    """
    >>> last([])
    Traceback (most recent call last):
    ...
    StopIteration
    >>> last([], None)
    >>> last([1, 2, 3])
    3
    >>> last(range(1, 4))
    3
    >>> # noinspection PyUnresolvedReferences
    >>> last(x for x in range(1, 4))
    3
    """
    items = iter(items)
    for item in items:
        break
    else:
        if default is NotImplemented:
            raise StopIteration()
        else:
            return default

    for item in items:
        pass

    return item


def iterable_length(iterable: Iterable[T]) -> int:
    """
    >>> iterable_length(range(5))
    5
    >>> iterable_length(range(-5))
    0
    >>> iterable_length((1, 2))
    2
    >>> iterable_length([1, 2])
    2
    """
    if hasattr(iterable, "__len__"):
        return len(cast(Sized, iterable))
    return sum(1 for _ in iterable)


def count_by(
    iterable: Iterable[T], key: Optional[Callable[[T], S]] = None,
) -> Dict[T, int]:
    """
    >>> count_by(range(5))
    {0: 1, 1: 1, 2: 1, 3: 1, 4: 1}
    >>> count_by(range(-5))
    {}
    >>> count_by((1, 2))
    {1: 1, 2: 1}
    >>> count_by([1, 2])
    {1: 1, 2: 1}
    >>> count_by([1, 2, 1, 2, 2])
    {1: 2, 2: 3}
    >>> count_by([1, 1, 1, 1, 1])
    {1: 5}
    """
    return {
        _key: iterable_length(items)
        for _key, items
        in itertools.groupby(sorted(iterable, key=key), key=key)
    }
