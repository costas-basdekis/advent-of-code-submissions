#!/usr/bin/env python3
import doctest
import functools
import itertools
import math
from copy import deepcopy

from utils import get_current_directory
from year_2019.day_12.part_a import make_moon, tick_moons, parse_simulation


def solve(_input=None):
    """
    >>> solve()
    282270365571288
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return find_repeat_count_intelligent(parse_simulation(_input))


def find_repeat_count_intelligent(moons):
    """
    >>> find_repeat_count_intelligent([])
    1
    >>> find_repeat_count_intelligent(parse_simulation(\
        "pos=<x= -1, y=  0, z=  2>, vel=<x=  0, y=  0, z=  0>\\n"\
        "pos=<x=  2, y=-10, z= -7>, vel=<x=  0, y=  0, z=  0>\\n"\
        "pos=<x=  4, y= -8, z=  8>, vel=<x=  0, y=  0, z=  0>\\n"\
        "pos=<x=  3, y=  5, z= -1>, vel=<x=  0, y=  0, z=  0>"))
    2772
    >>> find_repeat_count_intelligent(parse_simulation(\
        "<x=-8, y=-10, z=0>\\n"\
        "<x=5, y=5, z=10>\\n"\
        "<x=2, y=-7, z=3>\\n"\
        "<x=9, y=-8, z=-3>"))
    4686774924
    """
    counts = [
        find_repeat_count_naive([
            make_moon(
                (moon["position"][axis], 0, 0),
                (moon["velocity"][axis], 0, 0))
            for moon in moons
        ])
        for axis in ['x', 'y', 'z']
    ]
    return lcm(*counts)


def lcm(*values):
    """
    >>> lcm(5)
    5
    >>> lcm(5, 3)
    15
    >>> lcm(15, 3)
    15
    >>> lcm(5, 3, 15)
    15
    >>> lcm(12, 8, 9)
    72
    """
    if not values:
        raise Exception("At least 1 item is expected")
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        a, b = values
        return abs(a * b) // math.gcd(a, b)
    return functools.reduce(lcm, values)


def find_repeat_count_naive(moons):
    """
    >>> find_repeat_count_naive([])
    1
    >>> find_repeat_count_naive(parse_simulation(\
        "pos=<x= -1, y=  0, z=  2>, vel=<x=  0, y=  0, z=  0>\\n"\
        "pos=<x=  2, y=-10, z= -7>, vel=<x=  0, y=  0, z=  0>\\n"\
        "pos=<x=  4, y= -8, z=  8>, vel=<x=  0, y=  0, z=  0>\\n"\
        "pos=<x=  3, y=  5, z= -1>, vel=<x=  0, y=  0, z=  0>"))
    2772
    """
    seen_hashes = {hash_moons(moons)}
    moons = deepcopy(moons)
    for count in itertools.count(start=1):
        tick_moons(moons)
        moons_hash = hash_moons(moons)
        if moons_hash in seen_hashes:
            break
        seen_hashes.add(moons_hash)
    else:
        raise Exception("Finished infinite loop, or didn't loop at all")

    return count


def hash_moons(moons):
    """
    >>> hash_moons([\
        make_moon((1, 2, 3), (4, 5, 6)), make_moon((1, -2, 3), (-4, 5, -6))])
    '1,2,3:4,5,6|1,-2,3:-4,5,-6'
    """
    return "|".join(map(hash_moon, moons))


def hash_moon(moon):
    """
    >>> hash_moon(make_moon((1, 2, 3), (4, 5, 6)))
    '1,2,3:4,5,6'
    >>> hash_moon(make_moon((1, -2, 3), (-4, 5, -6)))
    '1,-2,3:-4,5,-6'
    """
    position = moon["position"]
    velocity = moon["velocity"]
    return (
        f"{position['x']},{position['y']},{position['z']}"
        f":{velocity['x']},{velocity['y']},{velocity['z']}"
    )


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
