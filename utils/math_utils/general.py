from typing import Any, TypeVar, Iterable, Tuple, Optional, Callable

__all__ = [
    'min_and_max',
    'min_and_max_tuples',
    'product',
]

T = TypeVar('T', bound=Any)


def min_and_max(
    values: Iterable[T], default: T = NotImplemented,
    key: Optional[Callable[[T], Any]] = None,
) -> Tuple[T, T]:
    """
    >>> min_and_max([])
    Traceback (most recent call last):
    ...
    ValueError: min_and_max() arg is an empty sequence
    >>> min_and_max([], None)
    (None, None)
    >>> min_and_max(range(5))
    (0, 4)
    >>> min_and_max(range(5), None)
    (0, 4)
    >>> min_and_max([1, 2, 4, 5, -1, 8, 2])
    (-1, 8)
    >>> # noinspection PyUnresolvedReferences
    >>> min_and_max(x for x in [1, 2, 4, 5, -1, 8, 2])
    (-1, 8)
    >>> # noinspection PyUnresolvedReferences
    >>> min_and_max((x for x in [1, 2, 4, 5, -1, 8, 2]), key=lambda x: -x)
    (8, -1)
    """
    values = iter(values)
    if default is NotImplemented:
        default_args = []
    else:
        default_args = [default]
    try:
        first_value = next(values, *default_args)
    except StopIteration:
        raise ValueError('min_and_max() arg is an empty sequence')
    min_value = max_value = first_value
    for value in values:
        min_value = min(min_value, value, key=key)
        max_value = max(max_value, value, key=key)

    return min_value, max_value


TupleT = TypeVar('TupleT', bound=Tuple)


def min_and_max_tuples(tuples: Iterable[TupleT],
                       default: TupleT = NotImplemented,
                       ) -> Tuple[TupleT, TupleT]:
    """
    >>> min_and_max_tuples([])
    Traceback (most recent call last):
    ...
    ValueError: min_and_max_tuples() arg is an empty sequence
    >>> # noinspection PyTypeChecker
    >>> min_and_max_tuples([1])
    Traceback (most recent call last):
    ...
    TypeError: min_and_max_tuples() arg is not a tuple sequence
    >>> min_and_max_tuples([], ())
    ((), ())
    >>> min_and_max_tuples([], (1, 2, 3))
    ((1, 2, 3), (1, 2, 3))
    >>> # noinspection PyUnresolvedReferences
    >>> min_and_max_tuples([(x, x + 10) for x in range(5)])
    ((0, 10), (4, 14))
    >>> # noinspection PyUnresolvedReferences
    >>> min_and_max_tuples([(x, x + 10) for x in range(5)], (1, 11))
    ((0, 10), (4, 14))
    >>> min_and_max_tuples([
    ...     (1, 11), (2, 12), (4, 14), (5, 15), (-1, -11), (8, 18), (2, 12)])
    ((-1, -11), (8, 18))
    >>> # noinspection PyUnresolvedReferences
    >>> min_and_max_tuples((x, x + 10) for x in range(5))
    ((0, 10), (4, 14))
    >>> from utils.point import Point2D
    >>> # noinspection PyUnresolvedReferences
    >>> min_and_max_tuples(Point2D(x, x + 10) for x in range(5))
    ((0, 10), (4, 14))
    """
    tuples = iter(tuples)
    if default is NotImplemented:
        default_args = []
    else:
        default_args = [default]
    try:
        first_tuple = next(tuples, *default_args)
    except StopIteration:
        raise ValueError('min_and_max_tuples() arg is an empty sequence')
    if not isinstance(first_tuple, tuple):
        raise TypeError('min_and_max_tuples() arg is not a tuple sequence')
    min_values = max_values = first_tuple
    for _tuple in tuples:
        if not isinstance(_tuple, tuple):
            raise TypeError('min_and_max_tuples() arg is not a tuple sequence')
        if len(_tuple) != len(first_tuple):
            raise TypeError(
                'min_and_max_tuples() arg is not a fixed length tuple sequence')
        min_values = tuple(
            min(min_value, value)
            for index, (value, min_value) in enumerate(zip(_tuple, min_values))
        )
        max_values = tuple(
            max(max_value, value)
            for index, (value, max_value) in enumerate(zip(_tuple, max_values))
        )

    return tuple(min_values), tuple(max_values)


def product(values: Iterable[T], default=1) -> T:
    """
    >>> product([])
    1
    >>> product([], 5)
    5
    >>> product([1, 2, 3], 5)
    6
    >>> product([1, 2, 3])
    6
    >>> product((2.5, 3.5, 7))
    61.25
    """
    values = iter(values)
    result = next(values, default)
    for value in values:
        result *= value

    return result
