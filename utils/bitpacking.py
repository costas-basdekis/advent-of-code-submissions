import math
from functools import reduce
from typing import List, Iterable

__all__ = ['int_to_bits', 'bits_to_int']


def int_to_bits(_int: int) -> List[int]:
    """
    >>> list(map(int_to_bits, range(8)))
    [[], [1], [2], [1, 2], [4], [1, 4], [2, 4], [1, 2, 4]]
    >>> int_to_bits(2 ** 16)
    [65536]
    >>> int_to_bits(2 ** 16 - 1)
    [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384,
        32768]
    """
    if not _int:
        return []
    bits = int(math.log(_int, 2) + 1)
    return [
        2 ** index
        for index in range(bits)
        if 2 ** index & _int
    ]


def bits_to_int(bits: Iterable[int]) -> int:
    """
    >>> list(map(bits_to_int,
    ...     [[], [1], [2], [1, 2], [4], [1, 4], [2, 4], [1, 2, 4]]))
    [0, 1, 2, 3, 4, 5, 6, 7]
    >>> bits_to_int([65536])
    65536
    >>> # noinspection PyUnresolvedReferences
    >>> bits_to_int(2 ** x for x in range(16))
    65535
    """
    return reduce(int.__or__, bits, 0)
