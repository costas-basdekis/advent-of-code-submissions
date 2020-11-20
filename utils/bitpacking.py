import math
from functools import reduce
from typing import Iterable, Callable, Optional

__all__ = ['int_to_bits', 'bits_to_int', 'get_bit_count']


Ints = Iterable[int]


def int_to_bits(number: int, container: Optional[Callable[[Ints], Ints]] = None,
                ) -> Ints:
    """
    >>> # noinspection PyUnresolvedReferences
    >>> [int_to_bits(x, list) for x in  range(8)]
    [[], [1], [2], [1, 2], [4], [1, 4], [2, 4], [1, 2, 4]]
    >>> int_to_bits(2 ** 16, list)
    [65536]
    >>> int_to_bits(2 ** 16 - 1, list)
    [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384,
        32768]
    """
    if not number:
        return []
    bit_count = int(math.log(number, 2))
    powers = map((2).__pow__, range(bit_count + 1))
    bits = filter(number.__and__, powers)
    if container is not None:
        bits = container(bits)

    return bits


def bits_to_int(bits: Ints) -> int:
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


def get_bit_count(number: int) -> int:
    """
    >>> # noinspection PyUnresolvedReferences
    >>> [get_bit_count(x) for x in  range(8)]
    [0, 1, 1, 2, 1, 2, 2, 3]
    >>> get_bit_count(2 ** 16)
    1
    >>> get_bit_count(2 ** 16 - 1)
    16
    """
    from utils import helper
    return helper.iterable_length(int_to_bits(number))
