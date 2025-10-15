import math
from dataclasses import dataclass
from itertools import count
from typing import Any, TypeVar, Iterable, List, Tuple, ClassVar, Set, Iterator, Optional

__all__ = [
    'get_non_co_primes',
    'solve_linear_congruence_system',
    'get_bezout_coefficients',
    'factorise',
    'PrimeGenerator',
]

import utils
from aox.challenge import Debugger

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


@dataclass
class PrimeGenerator:
    primes_list: ClassVar[List[int]] = []
    primes_set: ClassVar[Set[int]] = set()
    next_prime: ClassVar[int] = 2

    @classmethod
    def destructively_clear_cache(cls) -> None:
        pass
        cls.primes_list.clear()
        cls.primes_set.clear()
        cls.next_prime = 2

    def __iter__(self) -> Iterator[int]:
        """
        >>> PrimeGenerator.destructively_clear_cache()
        >>> [prime for _, prime in zip(range(10), PrimeGenerator())]
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        >>> [prime for _, prime in zip(range(10), PrimeGenerator())]
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        """
        yield from self.primes_list
        yield from self.iterate_new_primes(None)

    def fill_until(self, max_number: int, debugger: Debugger = Debugger(enabled=False)) -> None:
        """
        >>> PrimeGenerator.destructively_clear_cache()
        >>> PrimeGenerator().fill_until(15)
        >>> PrimeGenerator().primes_list
        [2, 3, 5, 7, 11, 13]
        >>> sorted(PrimeGenerator().primes_set)
        [2, 3, 5, 7, 11, 13]
        >>> PrimeGenerator().next_prime
        16
        >>> PrimeGenerator().fill_until(30)
        >>> PrimeGenerator().primes_list
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        >>> sorted(PrimeGenerator().primes_set)
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        >>> PrimeGenerator().next_prime
        31
        """
        if max_number < PrimeGenerator.next_prime:
            return
        new_primes = set(range(PrimeGenerator.next_prime, max_number + 1))
        for prime in debugger.stepping(PrimeGenerator.primes_list):
            if debugger.should_report():
                debugger.default_report_if(f"Removing {prime} multiples")
            for factor in range(1, max_number // prime + 1):
                if prime * factor in new_primes:
                    new_primes.remove(prime * factor)
        for number in debugger.stepping(range(PrimeGenerator.next_prime, max_number + 1)):
            if debugger.should_report():
                debugger.default_report_if(f"Removing {number} multiples")
            if number not in new_primes:
                continue
            for factor in range(2, max_number // number + 1):
                if number * factor in new_primes:
                    new_primes.remove(number * factor)
        PrimeGenerator.primes_list.extend(sorted(new_primes))
        PrimeGenerator.primes_set.update(new_primes)
        PrimeGenerator.next_prime = max_number + 1

    def iterate_new_primes(self, max_number: Optional[int], debugger: Debugger = Debugger(enabled=False)) -> Iterable[int]:
        """
        >>> PrimeGenerator.destructively_clear_cache()
        >>> list(PrimeGenerator().iterate_new_primes(15))
        [2, 3, 5, 7, 11, 13]
        >>> PrimeGenerator().primes_list
        [2, 3, 5, 7, 11, 13]
        >>> sorted(PrimeGenerator().primes_set)
        [2, 3, 5, 7, 11, 13]
        >>> PrimeGenerator().next_prime
        16
        >>> list(PrimeGenerator().iterate_new_primes(30))
        [17, 19, 23, 29]
        >>> PrimeGenerator().primes_list
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        >>> sorted(PrimeGenerator().primes_set)
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        >>> PrimeGenerator().next_prime
        31
        """
        if max_number is None:
            numbers = count(self.next_prime)
        else:
            if max_number < self.next_prime:
                return
            numbers = range(self.next_prime, max_number + 1)
        if debugger:
            debugger.default_report(f"Checking new prime numbers{f' until {max_number}' if max_number is not None else ''}")
        for number in debugger.stepping(numbers):
            is_prime = self.check_is_prime(number)
            if is_prime:
                PrimeGenerator.primes_list.append(number)
                PrimeGenerator.primes_set.add(number)
            PrimeGenerator.next_prime = number + 1
            if is_prime:
                yield number
            if debugger.should_report():
                debugger.default_report_if(f"Checked {number}{('/' + str(max_number)) if max_number is not None else ''}")

    def check_is_prime(self, number: int) -> bool:
        """
        >>> PrimeGenerator.destructively_clear_cache()
        >>> [_number for _number in range(31) if PrimeGenerator().check_is_prime(_number)]
        Traceback (most recent call last):
        ...
        Exception: You need to fill in at least up to 2
        >>> PrimeGenerator().fill_until(30)
        >>> [_number for _number in range(31) if PrimeGenerator().check_is_prime(_number)]
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        """
        if number < 2:
            return False
        if number > self.next_prime:
            raise Exception(f"You need to fill in at least up to {number - 1}")
        for prime in self.primes_list:
            if prime >= number:
                break
            if (number // prime) * prime == number:
                return False
        return True

    def __contains__(self, item: int) -> bool:
        """
        >>> PrimeGenerator.destructively_clear_cache()
        >>> [_number for _number in range(31) if _number in PrimeGenerator()]
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        >>> PrimeGenerator().primes_list
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        >>> sorted(PrimeGenerator().primes_set)
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        >>> PrimeGenerator().next_prime
        30
        """
        if item < self.next_prime:
            return item in self.primes_set
        self.fill_until(item - 1)
        return self.check_is_prime(item)
