#!/usr/bin/env python3
import doctest
import re
from copy import deepcopy

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    14809
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    moons_0 = parse_scan(_input)
    moons_1000 = repeat(tick_moons, 1000, moons_0)
    return get_moons_energy(moons_1000)


def get_moons_energy(moons):
    """
    >>> get_moons_energy([])
    0
    >>> get_moons_energy([make_moon((-1, -2, 3)), make_moon((2, 0, 4), (2, 0, 4))])
    36
    >>> get_moons_energy(parse_simulation(\
        "pos=<x= 2, y= 1, z=-3>, vel=<x=-3, y=-2, z= 1>\\n"\
        "pos=<x= 1, y=-8, z= 0>, vel=<x=-1, y= 1, z= 3>\\n"\
        "pos=<x= 3, y=-6, z= 1>, vel=<x= 3, y= 2, z=-3>\\n"\
        "pos=<x= 2, y= 0, z= 4>, vel=<x= 1, y=-1, z=-1>"))
    179
    >>> get_moons_energy(parse_simulation(\
        "pos=<x=  8, y=-12, z= -9>, vel=<x= -7, y=  3, z=  0>\\n"\
        "pos=<x= 13, y= 16, z= -3>, vel=<x=  3, y=-11, z= -5>\\n"\
        "pos=<x=-29, y=-11, z= -1>, vel=<x= -3, y=  7, z=  4>\\n"\
        "pos=<x= 16, y=-13, z= 23>, vel=<x=  7, y=  1, z=  1>"))
    1940
    """
    return sum(map(get_moon_energy, moons), 0)


def get_moon_energy(moon):
    """
    >>> get_moon_energy(make_moon((0, 0, 0)))
    0
    >>> get_moon_energy(make_moon((-1, -2, 3)))
    0
    >>> get_moon_energy(make_moon((1, 2, -3)))
    0
    >>> get_moon_energy(make_moon((0, 0, 0), (-1, -2, 3)))
    0
    >>> get_moon_energy(make_moon((0, 0, 0), (1, 2, -3)))
    0
    >>> get_moon_energy(make_moon((2, 0, 4), (2, 0, 4)))
    36
    >>> get_moon_energy(make_moon((2, 0, 4), (5, -3, 7)))
    90
    >>> get_moon_energy(parse_simulation(\
        "pos=<x= 2, y= 1, z=-3>, vel=<x=-3, y=-2, z= 1>")[0])
    36
    """
    return get_moon_potential_energy(moon) * get_moon_kinetic_energy(moon)


def get_moon_potential_energy(moon):
    """
    >>> get_moon_potential_energy(make_moon((0, 0, 0)))
    0
    >>> get_moon_potential_energy(make_moon((-1, -2, 3)))
    6
    >>> get_moon_potential_energy(make_moon((1, 2, -3)))
    6
    >>> get_moon_potential_energy(make_moon((2, 1, -3)))
    6
    >>> get_moon_potential_energy(make_moon((1, -8, 0)))
    9
    >>> get_moon_potential_energy(make_moon((3, -6, 1)))
    10
    >>> get_moon_potential_energy(make_moon((2, 0, 4)))
    6
    >>> get_moon_potential_energy(make_moon((2, 0, 4), (2, 0, 4)))
    6
    >>> get_moon_potential_energy(make_moon((2, 0, 4), (5, -3, 7)))
    6
    >>> get_moon_potential_energy(parse_simulation(\
        "pos=<x= 2, y= 1, z=-3>, vel=<x=-3, y=-2, z= 1>")[0])
    6
    """
    return sum(map(abs, moon["position"].values()))


def get_moon_kinetic_energy(moon):
    """
    >>> get_moon_kinetic_energy(make_moon((0, 0, 0), (0, 0, 0)))
    0
    >>> get_moon_kinetic_energy(make_moon((0, 0, 0), (-1, -2, 3)))
    6
    >>> get_moon_kinetic_energy(make_moon((0, 0, 0), (1, 2, -3)))
    6
    >>> get_moon_kinetic_energy(make_moon((0, 0, 0), (2, 1, -3)))
    6
    >>> get_moon_kinetic_energy(make_moon((0, 0, 0), (1, -8, 0)))
    9
    >>> get_moon_kinetic_energy(make_moon((0, 0, 0), (3, -6, 1)))
    10
    >>> get_moon_kinetic_energy(make_moon((0, 0, 0), (2, 0, 4)))
    6
    >>> get_moon_kinetic_energy(make_moon((2, 0, 4), (2, 0, 4)))
    6
    >>> get_moon_kinetic_energy(make_moon((5, -3, 7), (2, 0, 4)))
    6
    >>> get_moon_kinetic_energy(parse_simulation(\
        "pos=<x= 2, y= 1, z=-3>, vel=<x=-3, y=-2, z= 1>")[0])
    6
    """
    return sum(map(abs, moon["velocity"].values()))


def repeat(func, count, argument):
    """
    >>> repeat(lambda x: x + 2, 0, 1)
    1
    >>> repeat(lambda x: x + 2, 1, 1)
    3
    >>> repeat(lambda x: x + 2, 5, 1)
    11
    """
    result = argument
    for _ in range(count):
        result = func(result)
    return result


def tick_moons(moons):
    """
    >>> moons_a_0 = parse_simulation(\
        "pos=<x=-1, y=  0, z= 2>, vel=<x= 0, y= 0, z= 0>\\n"\
        "pos=<x= 2, y=-10, z=-7>, vel=<x= 0, y= 0, z= 0>\\n"\
        "pos=<x= 4, y= -8, z= 8>, vel=<x= 0, y= 0, z= 0>\\n"\
        "pos=<x= 3, y=  5, z=-1>, vel=<x= 0, y= 0, z= 0>")
    >>> moons_a_1 = tick_moons(deepcopy(moons_a_0))
    >>> moons_a_1 == parse_simulation(\
        "pos=<x= 2, y=-1, z= 1>, vel=<x= 3, y=-1, z=-1>\\n"\
        "pos=<x= 3, y=-7, z=-4>, vel=<x= 1, y= 3, z= 3>\\n"\
        "pos=<x= 1, y=-7, z= 5>, vel=<x=-3, y= 1, z=-3>\\n"\
        "pos=<x= 2, y= 2, z= 0>, vel=<x=-1, y=-3, z= 1>")
    True
    >>> moons_a_2 = tick_moons(deepcopy(moons_a_1))
    >>> moons_a_2 == parse_simulation(\
        "pos=<x= 5, y=-3, z=-1>, vel=<x= 3, y=-2, z=-2>\\n"\
        "pos=<x= 1, y=-2, z= 2>, vel=<x=-2, y= 5, z= 6>\\n"\
        "pos=<x= 1, y=-4, z=-1>, vel=<x= 0, y= 3, z=-6>\\n"\
        "pos=<x= 1, y=-4, z= 2>, vel=<x=-1, y=-6, z= 2>")
    True
    >>> moons_a_3 = tick_moons(deepcopy(moons_a_2))
    >>> moons_a_4 = tick_moons(deepcopy(moons_a_3))
    >>> moons_a_5 = tick_moons(deepcopy(moons_a_4))
    >>> moons_a_6 = tick_moons(deepcopy(moons_a_5))
    >>> moons_a_7 = tick_moons(deepcopy(moons_a_6))
    >>> moons_a_8 = tick_moons(deepcopy(moons_a_7))
    >>> moons_a_9 = tick_moons(deepcopy(moons_a_8))
    >>> moons_a_10 = tick_moons(deepcopy(moons_a_9))
    >>> moons_a_10 == parse_simulation(\
        "pos=<x= 2, y= 1, z=-3>, vel=<x=-3, y=-2, z= 1>\\n"\
        "pos=<x= 1, y=-8, z= 0>, vel=<x=-1, y= 1, z= 3>\\n"\
        "pos=<x= 3, y=-6, z= 1>, vel=<x= 3, y= 2, z=-3>\\n"\
        "pos=<x= 2, y= 0, z= 4>, vel=<x= 1, y=-1, z=-1>")
    True
    >>> moons_a_0 != moons_a_1 != moons_a_2 != moons_a_3 != moons_a_4 \
        != moons_a_5 != moons_a_6 != moons_a_7 != moons_a_8 != moons_a_9 \
        != moons_a_10
    True
    >>> moons_b_0 = parse_simulation(\
        "pos=<x= -8, y=-10, z=  0>, vel=<x=  0, y=  0, z=  0>\\n"\
        "pos=<x=  5, y=  5, z= 10>, vel=<x=  0, y=  0, z=  0>\\n"\
        "pos=<x=  2, y= -7, z=  3>, vel=<x=  0, y=  0, z=  0>\\n"\
        "pos=<x=  9, y= -8, z= -3>, vel=<x=  0, y=  0, z=  0>")
    >>> moons_b_100 = parse_simulation(\
        "pos=<x=  8, y=-12, z= -9>, vel=<x= -7, y=  3, z=  0>\\n"\
        "pos=<x= 13, y= 16, z= -3>, vel=<x=  3, y=-11, z= -5>\\n"\
        "pos=<x=-29, y=-11, z= -1>, vel=<x= -3, y=  7, z=  4>\\n"\
        "pos=<x= 16, y=-13, z= 23>, vel=<x=  7, y=  1, z=  1>")
    >>> repeat(tick_moons, 100, moons_b_0) == moons_b_100
    True
    """
    gravities = [
        get_total_gravity(moon, moons)
        for moon in moons
    ]
    for moon, gravity in zip(moons, gravities):
        apply_gravity(moon, gravity)
        apply_velocity(moon)

    return moons


def apply_velocity(moon):
    """
    >>> apply_velocity(make_moon((-1, 0, 2), (3, -1, -1)))
    {'position': {'x': 2, 'y': -1, 'z': 1}, 'velocity': {'x': 3, 'y': -1, 'z': -1}}
    """
    moon["position"]["x"] += moon["velocity"]["x"]
    moon["position"]["y"] += moon["velocity"]["y"]
    moon["position"]["z"] += moon["velocity"]["z"]

    return moon


def apply_gravity(moon, gravity):
    """
    >>> apply_gravity(make_moon((-1, 0, 2)), (3, -1, -1))
    {'position': {'x': -1, 'y': 0, 'z': 2}, 'velocity': {'x': 3, 'y': -1, 'z': -1}}
    >>> apply_gravity(apply_gravity(make_moon((-1, 0, 2)), (3, -1, -1)), (-2, 4, -7))
    {'position': {'x': -1, 'y': 0, 'z': 2}, 'velocity': {'x': 1, 'y': 3, 'z': -8}}
    """
    x, y, z = gravity
    moon["velocity"]["x"] += x
    moon["velocity"]["y"] += y
    moon["velocity"]["z"] += z

    return moon


def get_total_gravity(moon, moons):
    """
    >>> get_total_gravity(make_moon((1, 2, 3)), [])
    (0, 0, 0)
    >>> moons_a = parse_scan(\
        "<x=-1, y=0, z=2>\\n<x=2, y=-10, z=-7>\\n<x=4, y=-8, z=8>"\
        "\\n<x=3, y=5, z=-1>")
    >>> get_total_gravity(moons_a[0], moons_a)
    (3, -1, -1)
    >>> get_total_gravity(moons_a[1], moons_a)
    (1, 3, 3)
    >>> get_total_gravity(moons_a[2], moons_a)
    (-3, 1, -3)
    >>> get_total_gravity(moons_a[3], moons_a)
    (-1, -3, 1)
    """
    total_x, total_y, total_z = (0, 0, 0)
    for other in moons:
        x, y, z = get_pair_gravity(moon, other)
        total_x += x
        total_y += y
        total_z += z

    return total_x, total_y, total_z


def get_pair_gravity(moon, other):
    """
    >>> get_pair_gravity(make_moon((0, 0, 0)), make_moon((0, 0, 0)))
    (0, 0, 0)
    >>> get_pair_gravity(make_moon((0, 0, 0)), make_moon((1, 0, 0)))
    (1, 0, 0)
    >>> get_pair_gravity(make_moon((0, 0, 0)), make_moon((2, 3, 4)))
    (1, 1, 1)
    >>> get_pair_gravity(make_moon((0, 0, 0)), make_moon((-2, 3, -4)))
    (-1, 1, -1)
    >>> get_pair_gravity(make_moon((0, 0, 0)), make_moon((-2, 3, 0)))
    (-1, 1, 0)
    >>> get_pair_gravity(make_moon((-2, 3, 0)), make_moon((-2, 3, 0)))
    (0, 0, 0)
    >>> moon_a = make_moon((-2, 3, 0))
    >>> get_pair_gravity(moon_a, moon_a)
    (0, 0, 0)
    """
    if moon == other:
        return 0, 0, 0
    delta_x = sign(other["position"]["x"] - moon["position"]["x"])
    delta_y = sign(other["position"]["y"] - moon["position"]["y"])
    delta_z = sign(other["position"]["z"] - moon["position"]["z"])
    return delta_x, delta_y, delta_z


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


re_scan_line = re.compile(r"^<x=(-?\d+), y=(-?\d+), z=(-?\d+)>$")


def parse_scan(scan_text):
    """
    >>> parse_scan("")
    []
    >>> parse_scan("<x=0, y=6, z=1>")
    [{'position': {'x': 0, 'y': 6, 'z': 1}, 'velocity': {'x': 0, 'y': 0, 'z': 0}}]
    >>> parse_scan("<x=0, y=6, z=1>\\n\\n")
    [{'position': {'x': 0, 'y': 6, 'z': 1}, 'velocity': {'x': 0, 'y': 0, 'z': 0}}]
    >>> parse_scan(\
        "<x=-1, y=0, z=2>\\n<x=2, y=-10, z=-7>\\n<x=4, y=-8, z=8>"\
        "\\n<x=3, y=5, z=-1>")
    [\
{'position': {'x': -1, 'y': 0, 'z': 2}, 'velocity': {'x': 0, 'y': 0, 'z': 0}}, \
{'position': {'x': 2, 'y': -10, 'z': -7}, 'velocity': {'x': 0, 'y': 0, 'z': 0}}, \
{'position': {'x': 4, 'y': -8, 'z': 8}, 'velocity': {'x': 0, 'y': 0, 'z': 0}}, \
{'position': {'x': 3, 'y': 5, 'z': -1}, 'velocity': {'x': 0, 'y': 0, 'z': 0}}\
]
    """
    lines = scan_text.splitlines()
    non_empty_lines = filter(None, map(str.strip, lines))
    return [
        make_moon(position)
        for position in [
            map(int, re_scan_line.match(line).groups())
            for line in non_empty_lines
        ]
    ]


re_simulation_line = re.compile(
    r"^<x=\s*(-?\d+),\s*y=\s*(-?\d+),\s*z=\s*(-?\d+)>"
    r"|pos=<x=\s*(-?\d+),\s*y=\s*(-?\d+),\s*z=\s*(-?\d+)>"
    r",\s*vel=<x=\s*(-?\d+),\s*y=\s*(-?\d+),\s*z=\s*(-?\d+)>$")


def parse_simulation(scan_text):
    lines = scan_text.splitlines()
    non_empty_lines = filter(None, map(str.strip, lines))
    return [
        make_moon(position_or_both)
        if len(position_or_both) == 3 else
        make_moon(position_or_both[:3], position_or_both[3:])
        for position_or_both in [
            tuple(map(int, filter(
                None, re_simulation_line.match(line).groups())))
            for line in non_empty_lines
        ]
    ]


def make_moon(position, velocity=(0, 0, 0)):
    position_x, position_y, position_z = position
    velocity_x, velocity_y, velocity_z = velocity
    return {
        "position": {"x": position_x, "y": position_y, "z": position_z},
        "velocity": {"x": velocity_x, "y": velocity_y, "z": velocity_z},
    }


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
