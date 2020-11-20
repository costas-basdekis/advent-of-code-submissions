#!/usr/bin/env python3
import doctest
from abc import ABC
from collections import namedtuple

from utils import get_current_directory
from year_2020.day_12 import part_a


def solve(_input=None):
    """
    >>> solve()
    126797
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()

    return WaypointProgram.from_program_text(_input).run().manhattan_distance()


class WaypointShip(namedtuple("Ship", ("position", "waypoint")),
                   part_a.BaseShip):
    def __new__(cls, *args, **kwargs):
        """
        >>> WaypointShip()
        WaypointShip(position=(0, 0), waypoint=(10, -1))
        >>> WaypointShip(position=(2, 3))
        WaypointShip(position=(2, 3), waypoint=(10, -1))
        >>> WaypointShip((2, 3))
        WaypointShip(position=(2, 3), waypoint=(10, -1))
        >>> WaypointShip(waypoint=(-2, 3))
        WaypointShip(position=(0, 0), waypoint=(-2, 3))
        """
        if len(args) < 1:
            kwargs.setdefault("position", (0, 0))
        if len(args) < 3:
            kwargs.setdefault("waypoint", (10, -1))
        return super().__new__(cls, *args, **kwargs)

    def move(self, delta):
        """
        >>> WaypointShip().move((2, 3))
        WaypointShip(position=(0, 0), waypoint=(12, 2))
        >>> WaypointShip(waypoint=(4, 5)).move((2, 3))
        WaypointShip(position=(0, 0), waypoint=(6, 8))
        >>> WaypointShip(waypoint=(4, 5)).move((2, -3))
        WaypointShip(position=(0, 0), waypoint=(6, 2))
        """
        d_x, d_y = delta
        x, y = self.waypoint
        return self._replace(waypoint=(x + d_x, y + d_y))

    def move_forward(self, count):
        """
        >>> WaypointShip().move_forward(3)
        WaypointShip(position=(30, -3), waypoint=(10, -1))
        """
        x, y = self.position
        d_x, d_y = self.waypoint
        return self._replace(position=(x + d_x * count, y + d_y * count))

    def rotate(self, quarter_turns):
        """
        >>> WaypointShip().rotate(0)
        WaypointShip(position=(0, 0), waypoint=(10, -1))
        >>> WaypointShip().rotate(1)
        WaypointShip(position=(0, 0), waypoint=(1, 10))
        >>> WaypointShip().rotate(2)
        WaypointShip(position=(0, 0), waypoint=(-10, 1))
        >>> WaypointShip().rotate(3)
        WaypointShip(position=(0, 0), waypoint=(-1, -10))
        """
        quarter_turns = quarter_turns % 4
        x, y = self.waypoint
        if quarter_turns == 0:
            new_waypoint = x, y
        elif quarter_turns == 1:
            new_waypoint = -y, x
        elif quarter_turns == 2:
            new_waypoint = -x, -y
        elif quarter_turns == 3:
            new_waypoint = y, -x
        else:
            raise Exception(f"Quarter turns not in 0-3: {quarter_turns}")

        return self._replace(waypoint=new_waypoint)


class WaypointProgram(part_a.Program):
    """
    >>> WaypointProgram.from_program_text(
    ...     "F10\\nN3\\nF7\\nR90\\nF11\\n").run()
    WaypointShip(position=(214, 72), waypoint=(4, 10))
    """
    ship_class = WaypointShip


if __name__ == '__main__':
    if doctest.testmod(part_a).failed | doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
