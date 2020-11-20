#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2018.day_11 import part_a


def solve(_input=None):
    """
    >>> solve()
    42
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()


class FuelGridExtended(part_a.FuelGrid):
    def get_square_with_highest_power_level_among_all_sizes(self):
        """
        >>> FuelGridExtended(18)\\
        ...     .get_square_with_highest_power_level_among_all_sizes()
        ((90, 269, 16), 113)
        >>> FuelGridExtended(42)\\
        ...     .get_square_with_highest_power_level_among_all_sizes()
        ((232, 251, 12), 119)
        """
        if self.width != self.height:
            raise Exception("Can only run this on same width and height")

        def square_key(point_and_size):
            x, y, size = point_and_size
            return self.get_square_power_level(
                x, y, width=size, height=size)

        best_x, best_y, best_size = max((
            (x, y, size)
            for size in range(1, self.width + 1)
            for x in range(0, self.width - size + 1)
            for y in range(0, self.height - size + 1)
        ), key=square_key)
        square_power_level = self.get_square_power_level(
            best_x, best_y, width=best_size, height=best_size)
        return (best_x, best_y, best_size), square_power_level

    def get_square_power_level(self, start_x, start_y, width=3, height=3):
        """
        >>> FuelGridExtended(18).get_square_power_level(33, 45)
        29
        >>> FuelGridExtended(18).get_square_power_level(90, 269, 16, 16)
        113
        >>> FuelGridExtended(42).get_square_power_level(21, 61)
        30
        >>> FuelGridExtended(42).get_square_power_level(232, 251, 12, 12)
        119
        """
        return sum(
            self.get_power_level(x, y)
            for x in range(start_x, start_x + width)
            for y in range(start_y, start_y + height)
        )

    def get_square_power_level_with_columns(
            self, start_x, start_y, width, height):
        if (start_x, start_y) == (0, 0):
            return sum(
                self.get_column_power_level(start_x, y, width)
                for y in range(start_y, start_y + height)
            )

        return


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
