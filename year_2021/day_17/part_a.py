#!/usr/bin/env python3
from dataclasses import dataclass
import re
from itertools import count, chain
from typing import Iterable, List, Optional, Tuple, Union

import click

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        2628
        """
        return Launch.from_area_text(_input).find_highest_y_that_lands_in_area()

    OFFSET_MAP = {
        '\x1b[A': (0, -1),
        '\x1b[B': (0, 1),
        '\x1b[C': (1, 0),
        '\x1b[D': (-1, 0),
    }

    def play(self) -> None:
        launch = Launch.from_area_text(self.input)
        for y in range(0, 150):
            highest_y = launch\
                .get_highest_y_for_initial_y_that_lands_in_area_y(y)
            print(f"For y={y}: max={highest_y}")

        click.prompt("Visualise throw? Press any button")
        click.getchar()

        other_launch = Launch.from_area_text(
            "target area: x=20..30, y=-10..-5"
        )
        print(launch)
        initial_velocity: Point2D = Point2D(0, 0)
        while True:
            click.echo(f"Move initial velocity {initial_velocity}")
            char = click.getchar("Tell")
            if char == "q":
                break
            elif char == "s":
                launch, other_launch = other_launch, launch
            elif char in self.OFFSET_MAP:
                initial_velocity = initial_velocity.offset(
                    self.OFFSET_MAP[char],
                )
            else:
                continue
            launch.set_path_from(Point2D(0, 0), initial_velocity)
            print(launch)


@dataclass
class Area:
    min: Point2D
    max: Point2D

    re_area = re.compile(
        r"^target area: x=(-?\d+)..(-?\d+), y=(-?\d+)..(-?\d+)$"
    )

    @classmethod
    def from_area_text(cls, area_text: str) -> "Area":
        """
        >>> Area.from_area_text("target area: x=253..280, y=-73..-46")
        Area(min=Point2D(x=253, y=-73), max=Point2D(x=280, y=-46))
        """
        min_x, max_x, min_y, max_y = \
            map(int, cls.re_area.match(area_text).groups())

        return cls(min=Point2D(min_x, min_y), max=Point2D(max_x, max_y))

    def __iter__(self) -> Iterable[Point2D]:
        yield self.min
        yield self.max

    def __contains__(self, item: Point2D) -> bool:
        return (
            (self.min.x <= item.x <= self.max.x)
            and (self.min.y <= item.y <= self.max.y)
        )

    def with_zero_x(self) -> "Area":
        cls = type(self)
        # noinspection PyArgumentList
        return cls(
            min=Point2D(0, self.min.y),
            max=Point2D(0, self.max.y),
        )


@dataclass
class Launch:
    area: Area
    path: List[Point2D]

    @classmethod
    def from_area_text(cls, area_text: str) -> "Launch":
        return cls(
            area=Area.from_area_text(area_text),
            path=[Point2D.get_zero_point()],
        )

    def __str__(self) -> str:
        """
        >>> print(":", Launch(
        ...     area=Area.from_area_text("target area: x=20..30, y=-10..-5"),
        ...     path=[
        ...         Point2D(0, 0), Point2D(7, 2), Point2D(13, 3),
        ...         Point2D(18, 3), Point2D(22, 2), Point2D(25, 0),
        ...         Point2D(27, -3), Point2D(28, -7),
        ...     ],
        ... ))
        : .............#....#............
        .......#..............#........
        ...............................
        S........................#.....
        ...............................
        ...............................
        ...........................#...
        ...............................
        ....................TTTTTTTTTTT
        ....................TTTTTTTTTTT
        ....................TTTTTTTT#TT
        ....................TTTTTTTTTTT
        ....................TTTTTTTTTTT
        ....................TTTTTTTTTTT
        """
        (min_x, min_y), (max_x, max_y) = \
            min_and_max_tuples(self.path + list(self.area))
        if self.path:
            start = self.path[0]
        else:
            start = None
        return "\n".join(
            "".join(
                "S"
                if point == start else
                "#"
                if point in self.path else
                "T"
                if point in self.area else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
            )
            for y in range(max_y, min_y - 1, -1)
        )

    def find_highest_y_that_lands_in_area(self) -> int:
        """
        >>> Launch.from_area_text("target area: x=20..30, y=-10..-5")\\
        ...     .find_highest_y_that_lands_in_area()
        45
        """
        return max(filter(None, (
            self.get_highest_y_for_initial_y_that_lands_in_area_y(y)
            for y in range(self.area.min.y, self.area.min.y + 200)
        )))

    def with_zero_x_area(self) -> "Launch":
        cls = type(self)
        # noinspection PyArgumentList
        return cls(
            area=self.area.with_zero_x(),
            path=[Point2D.get_zero_point()],
        )

    def get_highest_y_for_initial_y_that_lands_in_area_y(
        self, initial_y: int,
    ) -> Optional[int]:
        if not (self.area.min.x == self.area.max.x == 0):
            return self\
                .with_zero_x_area()\
                .get_highest_y_for_initial_y_that_lands_in_area_y(initial_y)

        path = self.generate_path(
            Point2D.get_zero_point(),
            Point2D(0, initial_y),
        )
        last_point = path[-1]
        if last_point not in self.area:
            return None
        _, (_, max_y) = min_and_max_tuples(path)
        return max_y

    def set_path_from(
        self, initial_position: Point2D, initial_velocity: Point2D,
    ) -> "Launch":
        """
        >>> print(
        ...     ":",
        ...     Launch.from_area_text("target area: x=20..30, y=-10..-5")
        ...     .set_path_from(Point2D(0, 0), Point2D(6, 3)),
        ... )
        : ...............#..#............
        ...........#........#..........
        ...............................
        ......#..............#.........
        ...............................
        ...............................
        S....................#.........
        ...............................
        ...............................
        ...............................
        .....................#.........
        ....................TTTTTTTTTTT
        ....................TTTTTTTTTTT
        ....................TTTTTTTTTTT
        ....................TTTTTTTTTTT
        ....................T#TTTTTTTTT
        ....................TTTTTTTTTTT
        >>> print(
        ...     ":",
        ...     Launch.from_area_text("target area: x=20..30, y=-10..-5")
        ...     .set_path_from(Point2D(0, 0), Point2D(9, 0)),
        ... )
        : S........#.....................
        .................#.............
        ...............................
        ........................#......
        ...............................
        ....................TTTTTTTTTTT
        ....................TTTTTTTTTT#
        ....................TTTTTTTTTTT
        ....................TTTTTTTTTTT
        ....................TTTTTTTTTTT
        ....................TTTTTTTTTTT
        >>> print(
        ...     ":",
        ...     Launch.from_area_text("target area: x=20..30, y=-10..-5")
        ...     .set_path_from(Point2D(0, 0), Point2D(17, -4)),
        ... )
        : S................................................
        .................................................
        .................................................
        .................................................
        .................#...............................
        ....................TTTTTTTTTTT..................
        ....................TTTTTTTTTTT..................
        ....................TTTTTTTTTTT..................
        ....................TTTTTTTTTTT..................
        ....................TTTTTTTTTTT..#...............
        ....................TTTTTTTTTTT..................
        .................................................
        .................................................
        .................................................
        .................................................
        ................................................#
        """
        self.path = self.generate_path(initial_position, initial_velocity)
        return self

    def generate_path(
        self, initial_position: Point2D, initial_velocity: Point2D,
    ) -> List[Point2D]:
        """
        >>> Launch.from_area_text("target area: x=20..30, y=-10..-5")\\
        ...     .generate_path(Point2D(0, 0), Point2D(7, 2))
        [Point2D(x=0, y=0), Point2D(x=7, y=2), Point2D(x=13, y=3),
            Point2D(x=18, y=3), Point2D(x=22, y=2), Point2D(x=25, y=0),
            Point2D(x=27, y=-3), Point2D(x=28, y=-7)]
        """
        iter_path = self.iterate_path(initial_position, initial_velocity)
        path = []
        for position, velocity in iter_path:
            path.append(position)
            if position in self.area:
                break
            if position.y < self.area.min.y and velocity.y < 0:
                break

        return path

    def iterate_path(
        self, initial_position: Point2D, initial_velocity: Point2D,
    ) -> Iterable[Tuple[Point2D, Point2D]]:
        positions_and_velocities = zip(
            self.iterate_x_path(initial_position, initial_velocity),
            self.iterate_y_path(initial_position, initial_velocity),
        )
        for (x, v_x), (y, v_y) in positions_and_velocities:
            position = Point2D(x, y)
            velocity = Point2D(v_x, v_y)
            yield position, velocity

    def iterate_x_path(
        self, initial_position: Point2D, initial_velocity: Point2D,
    ) -> Iterable[Tuple[int]]:
        if initial_velocity.x >= 0:
            sign = -1
        else:
            sign = 1

        def get_x(n: int) -> int:
            return int(
                initial_position.x
                + n / 2 * (2 * initial_velocity.x + (n - 1) * sign)
            )
        v_xs = range(initial_velocity.x, 0, sign)
        x_s = map(get_x, range(abs(initial_velocity.x)))
        x_s = chain(
            x_s,
            (
                get_x(abs(initial_velocity.x))
                for _ in count()
            )
        )
        v_xs = chain(
            v_xs,
            (0 for _ in count()),
        )

        for x, v_x in zip(x_s, v_xs):
            yield x, v_x

    def iterate_y_path(
        self, initial_position: Point2D, initial_velocity: Point2D,
    ) -> Iterable[Tuple[int]]:
        v_ys = count(initial_velocity.y, -1)
        y_s = (
            int(initial_position.y + n / 2 * (2 * initial_velocity.y + 1 - n))
            for n in count()
        )
        for y, v_y in zip(y_s, v_ys):
            yield y, v_y


Challenge.main()
challenge = Challenge()
