#!/usr/bin/env python3
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        '243,34'
        """
        (best_x, best_y), _ = FuelGrid(int(_input))\
            .get_square_with_highest_power_level()

        return f"{best_x},{best_y}"


class FuelGrid(namedtuple("FuelGrid", ("serial_number", "width", "height"))):
    def __new__(cls, serial_number, width=300, height=300):
        # noinspection PyArgumentList
        return super().__new__(cls, serial_number, width, height)

    def __init__(self, *args, **kwargs):
        # noinspection PyArgumentList
        super().__init__()
        self.memoized_power_levels = {}

    def get_square_with_highest_power_level(self, width=3, height=3):
        """
        >>> FuelGrid(18).get_square_with_highest_power_level()
        ((33, 45), 29)
        >>> FuelGrid(42).get_square_with_highest_power_level()
        ((21, 61), 30)
        """
        def square_key(point):
            x, y = point
            return self.get_square_power_level(
                x, y, width=width, height=height)

        best_x, best_y = max((
            (x, y)
            for x in range(0, self.width - width + 1)
            for y in range(0, self.height - height + 1)
        ), key=square_key)
        square_power_level = self.get_square_power_level(
            best_x, best_y, width=width, height=height)
        return (best_x, best_y), square_power_level

    def get_square_power_level(self, start_x, start_y, width=3, height=3):
        """
        >>> FuelGrid(18).get_square_power_level(33, 45)
        29
        >>> FuelGrid(18).get_square_power_level(90, 269, 16, 16)
        113
        >>> FuelGrid(42).get_square_power_level(21, 61)
        30
        >>> FuelGrid(42).get_square_power_level(232, 251, 12, 12)
        119
        """
        return sum(
            self.get_power_level(x, y)
            for x in range(start_x, start_x + width)
            for y in range(start_y, start_y + height)
        )

    def get_memoized_power_level(self, x, y):
        if (x, y) not in self.memoized_power_levels:
            self.memoized_power_levels[(x, y)] = self.get_power_level(x, y)

        return self.memoized_power_levels[(x, y)]

    def get_power_level(self, x, y):
        return FuelCell(x, y, self.serial_number).get_power_level()


class FuelCell(namedtuple("FuelCell", ("x", "y", "grid_serial_number"))):
    def get_power_level(self):
        """
        >>> FuelCell(3, 5, 8).get_power_level()
        4
        >>> FuelCell(122, 79, 57).get_power_level()
        -5
        >>> FuelCell(217, 196, 39).get_power_level()
        0
        >>> FuelCell(101, 153, 71).get_power_level()
        4
        """
        rack_id = self.x + 10
        power_level = rack_id * self.y
        power_level += self.grid_serial_number
        power_level *= rack_id
        power_level = (power_level // 100) % 10
        power_level -= 5

        return power_level


Challenge.main()
challenge = Challenge()
