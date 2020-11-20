#!/usr/bin/env python3
import doctest
import itertools
import math

from utils import get_current_directory
from year_2020.day_13 import part_a


def solve(_input=None):
    """
    >>> solve()
    725169163285238
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()

    return ScheduleExtended.from_schedule_text(_input)\
        .get_earliest_timestamp_with_dotted_departures()


class ScheduleExtended(part_a.Schedule):
    def get_earliest_timestamp_with_dotted_departures(self):
        """
        >>> ScheduleExtended.from_buses_text("7,13,x,x,59,x,31,19")\\
        ...     .get_earliest_timestamp_with_dotted_departures()
        1068781
        >>> ScheduleExtended.from_buses_text("17,x,13,19")\\
        ...     .get_earliest_timestamp_with_dotted_departures()
        3417
        >>> ScheduleExtended.from_buses_text("67,7,59,61")\\
        ...     .get_earliest_timestamp_with_dotted_departures()
        754018
        >>> ScheduleExtended.from_buses_text("67,x,7,59,61")\\
        ...     .get_earliest_timestamp_with_dotted_departures()
        779210
        >>> ScheduleExtended.from_buses_text("67,7,x,59,61")\\
        ...     .get_earliest_timestamp_with_dotted_departures()
        1261476
        >>> ScheduleExtended.from_buses_text("1789,37,47,1889")\\
        ...     .get_earliest_timestamp_with_dotted_departures()
        1202161486
        """
        return solve_linear_congruence_system([
            (bus_number, bus_number - index)
            for bus_number, index in self.bus_numbers_and_indexes.items()
        ])


def solve_linear_congruence_system(divisors_and_remainders):
    """
    >>> solve_linear_congruence_system([(3, 2), (5, 3), (7, 2)])
    23
    """
    divisors = [
        divisor
        for divisor, _ in divisors_and_remainders
    ]
    non_co_prime_divisors = get_non_co_primes(divisors)
    if non_co_prime_divisors:
        raise Exception(
            f"Some divisors are not co-prime: {non_co_prime_divisors}")
    divisors_product = product(divisors)
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


def get_bezout_coefficients(a, b):
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


def get_non_co_primes(items):
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
    items_product = product(items)
    return [
        item
        for item in items
        if math.gcd(item, items_product // item) != 1
    ]


def product(items):
    """
    >>> product([])
    1
    >>> product([0, 1, 2])
    0
    >>> product([3, 4, 5, 6])
    360
    """
    items_product = 1
    for item in items:
        items_product *= item

    return items_product


if __name__ == '__main__':
    if doctest.testmod(part_a).failed | doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
