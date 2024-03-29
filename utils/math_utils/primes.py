import math
from typing import Any, TypeVar, Iterable, List, Tuple

__all__ = [
    'get_non_co_primes',
    'solve_linear_congruence_system',
    'get_bezout_coefficients',
    'factorise',
]

import utils

T = TypeVar('T', bound=Any)


def get_non_co_primes(items: Iterable[int]) -> List[int]:
    """
    >>> get_non_co_primes([])
    []
    >>> get_non_co_primes([2, 3, 5])
    []
    >>> get_non_co_primes([2, 3, 4])
    [2, 4]
    >>> get_non_co_primes([3, 4, 5, 6])
    [3, 4, 6]
    """
    items_product = utils.product(items)
    return [
        item
        for item in items
        if math.gcd(item, items_product // item) != 1
    ]


def solve_linear_congruence_system(
        divisors_and_remainders: Iterable[Tuple[int, int]]) -> int:
    """
    >>> solve_linear_congruence_system([(3, 2), (5, 3), (7, 2)])
    23
    """
    divisors = [
        divisor
        for divisor, _ in divisors_and_remainders
    ]
    non_co_prime_divisors = utils.get_non_co_primes(divisors)
    if non_co_prime_divisors:
        raise Exception(
            f"Some divisors are not co-prime: {non_co_prime_divisors}")
    divisors_product = utils.product(divisors)
    coefficients_pairs = (
        get_bezout_coefficients(divisor, divisors_product // divisor)
        for divisor in divisors
    )

    a_solution = sum(
        remainder * coefficient * divisors_product // divisor
        for (divisor, remainder), (_, coefficient)
        in zip(divisors_and_remainders, coefficients_pairs)
    )

    return a_solution % divisors_product


def get_bezout_coefficients(a: int, b: int) -> Tuple[int, int]:
    """
    >>> get_bezout_coefficients(3, 4)
    (-1, 1)
    >>> get_bezout_coefficients(5, 12)
    (5, -2)
    >>> get_bezout_coefficients(240, 46)
    (-9, 47)
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    return old_s, old_t


def factorise(number: int) -> Iterable[int]:
    """
    >>> sorted(factorise(1))
    [1]
    >>> sorted(factorise(2))
    [1, 2]
    >>> sorted(factorise(5))
    [1, 5]
    >>> sorted(factorise(9))
    [1, 3, 9]
    >>> sorted(factorise(10))
    [1, 2, 5, 10]
    >>> sorted(factorise(100))
    [1, 2, 4, 5, 10, 20, 25, 50, 100]
    """
    root_or_less = int(math.sqrt(number))
    for divisor in range(1, root_or_less):
        if number % divisor == 0:
            yield divisor
            yield number // divisor

    if number % root_or_less == 0:
        yield root_or_less
        if root_or_less * root_or_less != number:
            yield number // root_or_less
