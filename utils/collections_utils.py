from typing import Iterable, Tuple, TypeVar

__all__ = ['KeyedDefaultDict', 'in_groups', 'get_fixed_length_substrings']


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


T = TypeVar('T')


def in_groups(iterable: Iterable[T], size: int) -> Iterable[Tuple[T, ...]]:
    """
    >>> list(in_groups([], 3))
    []
    >>> list(in_groups(range(5), 3))
    [(0, 1, 2), (3, 4)]
    >>> # noinspection PyUnresolvedReferences
    >>> list(in_groups((x for x in range(5)), 3))
    [(0, 1, 2), (3, 4)]
    >>> # noinspection PyUnresolvedReferences
    >>> list(in_groups((x for x in range(6)), 3))
    [(0, 1, 2), (3, 4, 5)]
    >>> # noinspection PyUnresolvedReferences
    >>> list(in_groups((x for x in range(5)), 6))
    [(0, 1, 2, 3, 4)]
    >>> # noinspection PyUnresolvedReferences
    >>> list(in_groups((x for x in range(5)), 10))
    [(0, 1, 2, 3, 4)]
    """
    if size < 1:
        raise ValueError(f"Expected size larger than 0, got {size}")
    group = ()
    for item in iterable:
        group += (item,)
        if len(group) >= size:
            yield group
            group = ()
    if group:
        yield group


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
