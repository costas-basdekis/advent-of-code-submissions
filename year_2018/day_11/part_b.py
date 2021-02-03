#!/usr/bin/env python3
import itertools

import utils

from year_2018.day_11 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        '90,214,15'
        """
        (x, y, size), _ = FuelGridExtended(int(_input))\
            .get_square_with_highest_power_level_among_all_sizes()

        return f"{x},{y},{size}"


class FuelGridExtended(part_a.FuelGrid):
    def get_column(self, x, y, size):
        return sum(
            self.get_memoized_power_level(x, cell_y)
            for cell_y in range(y, y + size)
        )

    def get_square_with_highest_power_level_among_all_sizes(self):
        """"""
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

        def square_key(point_size_and_level):
            _, _, _, level = point_size_and_level
            return level

        best_x, best_y, best_size, _ = max((
            ((x, y) + self.get_size_with_highest_power_level_for_point(
                x, y))
            for x in range(self.width)
            for y in range(self.height)
        ), key=square_key)
        square_power_level = self.get_square_power_level(
            best_x, best_y, width=best_size, height=best_size)
        return (best_x, best_y, best_size), square_power_level

    def get_size_with_highest_power_level_for_point(self, x, y):
        """
        >>> FuelGridExtended(18)\\
        ...     .get_size_with_highest_power_level_for_point(90, 269)[0]
        16
        >>> FuelGridExtended(42)\\
        ...     .get_size_with_highest_power_level_for_point(232, 251)[0]
        12
        """
        if self.width != self.height:
            raise Exception("Can only run this on same width and height")

        def get_power_level(size_and_power_level):
            _, power_level = size_and_power_level

            return power_level

        return max(
            self.get_sizes_and_power_levels_for_point(x, y),
            key=get_power_level)

    def get_sizes_and_power_levels_for_point(self, x, y):
        if self.width != self.height:
            raise Exception("Can only run this on same width and height")

        max_size = min(self.width - x, self.height - y)
        total_power_level = 0
        for size in range(0, max_size):
            total_power_level += sum(
                self.get_memoized_power_level(cell_x, cell_y)
                for cell_x, cell_y
                in self.get_points_for_square_border(x, y, size)
            )
            yield size, total_power_level

    def get_points_for_square_border(self, x, y, size):
        """
        >>> sorted(FuelGridExtended(0).get_points_for_square_border(0, 0, 1))
        [(0, 0)]
        >>> sorted(FuelGridExtended(0).get_points_for_square_border(3, 5, 1))
        [(3, 5)]
        >>> sorted(FuelGridExtended(0).get_points_for_square_border(0, 0, 2))
        [(0, 1), (1, 0), (1, 1)]
        >>> sorted(FuelGridExtended(0).get_points_for_square_border(0, 0, 4))
        [(0, 3), (1, 3), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3)]
        >>> sorted(FuelGridExtended(0).get_points_for_square_border(3, 5, 4))
        [(3, 8), (4, 8), (5, 8), (6, 5), (6, 6), (6, 7), (6, 8)]
        """
        return itertools.chain((
            (x + size - 1, cell_y)
            for cell_y in range(y, y + size)
        ), (
            (cell_x, y + size - 1)
            for cell_x in range(x, x + size - 1)
        ))


Challenge.main()
challenge = Challenge()
