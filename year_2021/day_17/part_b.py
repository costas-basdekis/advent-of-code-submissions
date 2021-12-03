#!/usr/bin/env python3
import math
from typing import Iterable, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, iterable_length
from year_2021.day_17.part_a import Launch


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1334
        """
        return LaunchExtended\
            .from_area_text(_input)\
            .get_initial_velocity_count_that_land_in_area()


class LaunchExtended(Launch):
    def get_initial_velocity_count_that_land_in_area(self) -> int:
        """
        >>> LaunchExtended.from_area_text("target area: x=20..30, y=-10..-5")\\
        ...     .get_initial_velocity_count_that_land_in_area()
        112
        """
        return iterable_length(self.get_initial_velocities_that_land_in_area())

    def get_initial_velocities_that_land_in_area(self) -> Iterable[Point2D]:
        return (
            Point2D(x, y)
            for y in range(self.area.min.y, self.area.min.y + 200)
            if self.get_highest_y_for_initial_y_that_lands_in_area_y(y)
            is not None
            for x in self.get_xs_that_land_in_area_for_initial_y(y)
        )

    def get_xs_that_land_in_area_for_initial_y(
        self, initial_y: int,
    ) -> Iterable[int]:
        if Point2D(0, self.area.min.y) in self.area:
            xs = range(self.area.min.x, self.area.max.x + 1)
        elif self.area.min.x > 0:
            min_x = math.floor((-1 + math.sqrt(1 + 8 * self.area.min.x)) / 2)
            xs = range(min_x, min_x + 500)
        else:
            max_x = math.floor((-1 - math.sqrt(1 + 8 * self.area.min.x)) / 2)
            xs = range(max_x, max_x - 500, -1)

        return (
            x
            for x in xs
            if self.does_path_land_in_area(Point2D(x, initial_y))
        )

    def does_path_land_in_area(self, initial_velocity: Point2D) -> bool:
        path = self.generate_path(Point2D.get_zero_point(), initial_velocity)
        last_point = path[-1]
        return last_point in self.area


Challenge.main()
challenge = Challenge()
