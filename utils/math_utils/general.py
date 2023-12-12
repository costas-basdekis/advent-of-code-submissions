import functools

import math
from typing import Any, TypeVar, Iterable, Tuple, Optional, Callable

__all__ = [
    'min_and_max',
    'min_and_max_tuples',
    'product',
    'lcm',
    'sign',
    'reframe',
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
    TypeError: min_and_max_tuples() arg is not a tuple sequence, but int
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
    (Point2D(x=0, y=10), Point2D(x=4, y=14))
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
        raise TypeError(
            f'min_and_max_tuples() arg is not a tuple sequence, but '
            f'{type(first_tuple).__name__} '
        )
    min_values = max_values = first_tuple
    for _tuple in tuples:
        if not isinstance(_tuple, tuple):
            raise TypeError(
                f'min_and_max_tuples() arg is not a tuple sequence, but '
                f'{type(_tuple).__name__}'
            )
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

    tuple_type = type(first_tuple)
    return tuple_type(min_values), tuple_type(max_values)


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


def lcm(*items: int) -> int:
    """
    >>> lcm(2, 3)
    6
    >>> lcm(4, 6)
    12
    >>> lcm(2, 5)
    10
    >>> lcm(6, 5)
    30
    >>> lcm(2, 15)
    30
    >>> lcm(6, 15)
    30
    >>> lcm(100, 150, 200)
    600
    """
    if hasattr(math, "lcm"):
        return math.lcm(*items)
    result = 1
    for item in items:
        result = result * item // math.gcd(result, item)
    return result


def sign(value):
    """
    >>> sign(-5)
    -1
    >>> sign(-5000)
    -1
    >>> sign(-0.0001)
    -1
    >>> sign(0)
    0
    >>> sign(0.0)
    0
    >>> sign(+0)
    0
    >>> sign(-0)
    0
    >>> sign(5)
    1
    >>> sign(5000)
    1
    >>> sign(0.0001)
    1
    """
    if value < 0:
        return -1
    elif value == 0:
        return 0
    else:
        return 1


def reframe(source_value: float, source_min: float, source_max: float, target_min: float, target_max: float) -> float:
    """
    >>> [reframe(x, 0, 10, 0, 100) for x in [-25, -10, -5, 0, 1, 5, 6, 10, 15, 20, 35]]
    [-250.0, -100.0, -50.0, 0.0, 10.0, 50.0, 60.0, 100.0, 150.0, 200.0, 350.0]
    >>> [reframe(x, 0, 10, 100, 200) for x in [-25, -10, -5, 0, 1, 5, 6, 10, 15, 20, 35]]
    [-150.0, 0.0, 50.0, 100.0, 110.0, 150.0, 160.0, 200.0, 250.0, 300.0, 450.0]
    """
    target_length = target_max - target_min
    source_length = source_max - source_min
    return (source_value - source_min) * target_length / source_length + target_min

