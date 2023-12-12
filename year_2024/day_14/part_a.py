#!/usr/bin/env python3
from dataclasses import dataclass
import re
from itertools import groupby
from typing import ClassVar, Generic, List, Type, Union, TypeVar

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, get_type_argument_class, Cls, Self, product


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        222062148
        """
        return Space.from_text(_input).move(100).get_safety_factor()


RobotT = TypeVar('RobotT', bound="Robot")


@dataclass
class Space(Generic[RobotT]):
    robots: List[RobotT]
    width: int
    height: int

    @classmethod
    def get_robot_class(cls) -> Type[RobotT]:
        # noinspection PyTypeChecker
        return get_type_argument_class(cls, RobotT)

    @classmethod
    def from_text(cls, text: str, width: int = 101, height: int = 103) -> "Space":
        """
        >>> print(Space.from_text('''
        ...     p=0,4 v=3,-3
        ...     p=6,3 v=-1,-3
        ...     p=10,3 v=-1,2
        ...     p=2,0 v=2,-1
        ...     p=0,0 v=1,3
        ...     p=3,0 v=-2,-2
        ...     p=7,6 v=-1,-3
        ...     p=3,0 v=-1,-2
        ...     p=9,3 v=2,3
        ...     p=7,3 v=-1,2
        ...     p=2,4 v=2,-3
        ...     p=9,5 v=-3,-3
        ... ''', 11, 7))
        1.12.......
        ...........
        ...........
        ......11.11
        1.1........
        .........1.
        .......1...
        """
        robot_class = cls.get_robot_class()
        return cls(
            robots=list(map(robot_class.from_text, text.strip().splitlines())),
            width=width,
            height=height,
        )

    def __str__(self) -> str:
        (min_x, min_y), (max_x, max_y) = (0, 0), (self.width - 1, self.height - 1)
        by_position = lambda robot: robot.position
        counts_by_position = {
            position: len(list(items))
            for position, items in groupby(sorted(self.robots, key=by_position), by_position)
        }
        return "\n".join(
            "".join(
                str(counts_by_position[point])
                if point in counts_by_position else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
            )
            for y in range(min_y, max_y+1)
        )

    def move(self: Self["Space"], count: int) -> Self["Space"]:
        """
        >>> print("!" + str(Space.from_text('''
        ...     p=0,4 v=3,-3
        ...     p=6,3 v=-1,-3
        ...     p=10,3 v=-1,2
        ...     p=2,0 v=2,-1
        ...     p=0,0 v=1,3
        ...     p=3,0 v=-2,-2
        ...     p=7,6 v=-1,-3
        ...     p=3,0 v=-1,-2
        ...     p=9,3 v=2,3
        ...     p=7,3 v=-1,2
        ...     p=2,4 v=2,-3
        ...     p=9,5 v=-3,-3
        ... ''', 11, 7).move(100)))
        !......2..1.
        ...........
        1..........
        .11........
        .....1.....
        ...12......
        .1....1....
        """
        cls = type(self)
        # noinspection PyArgumentList
        return cls(
            robots=[
                robot.move(count, self.width, self.height)
                for robot in self.robots
            ],
            width=self.width,
            height=self.height,
        )

    def get_safety_factor(self) -> int:
        """
        >>> Space.from_text('''
        ...     p=0,4 v=3,-3
        ...     p=6,3 v=-1,-3
        ...     p=10,3 v=-1,2
        ...     p=2,0 v=2,-1
        ...     p=0,0 v=1,3
        ...     p=3,0 v=-2,-2
        ...     p=7,6 v=-1,-3
        ...     p=3,0 v=-1,-2
        ...     p=9,3 v=2,3
        ...     p=7,3 v=-1,2
        ...     p=2,4 v=2,-3
        ...     p=9,5 v=-3,-3
        ... ''', 11, 7).move(100).get_safety_factor()
        12
        """
        return product(self.get_quadrant_counts())

    def get_quadrant_counts(self) -> List[int]:
        """
        >>> sorted(Space.from_text('''
        ...     p=0,4 v=3,-3
        ...     p=6,3 v=-1,-3
        ...     p=10,3 v=-1,2
        ...     p=2,0 v=2,-1
        ...     p=0,0 v=1,3
        ...     p=3,0 v=-2,-2
        ...     p=7,6 v=-1,-3
        ...     p=3,0 v=-1,-2
        ...     p=9,3 v=2,3
        ...     p=7,3 v=-1,2
        ...     p=2,4 v=2,-3
        ...     p=9,5 v=-3,-3
        ... ''', 11, 7).move(100).get_quadrant_counts())
        [1, 1, 3, 4]
        """
        mid_width = self.width // 2
        mid_height = self.height // 2
        quadrant_ranges = [
            (range(0, mid_width), range(0, mid_height)),
            (range(0, mid_width), range(mid_height + 1, self.height)),
            (range(mid_width + 1, self.width), range(mid_height + 1, self.height)),
            (range(mid_width + 1, self.width), range(0, mid_height)),
        ]
        by_position = lambda robot: robot.position
        counts_by_position = {
            position: len(list(items))
            for position, items in groupby(sorted(self.robots, key=by_position), by_position)
        }
        return [
            sum(
                counts_by_position.get(Point2D(x, y), 0)
                for x in x_range
                for y in y_range
            )
            for x_range, y_range in quadrant_ranges
        ]


@dataclass
class Robot:
    position: Point2D
    velocity: Point2D

    re_robot: ClassVar[re.Pattern] = re.compile(r"^p=(\d+),(\d+) v=(-?\d+),(-?\d+)$")

    @classmethod
    def from_text(cls: Cls["Robot"], text: str) -> Self["Robot"]:
        """
        >>> Robot.from_text("p=0,4 v=3,-3")
        Robot(position=Point2D(x=0, y=4), velocity=Point2D(x=3, y=-3))
        """
        str_values = cls.re_robot.match(text.strip()).groups()
        px, py, vx, vy = map(int, str_values)
        return cls(position=Point2D(px, py), velocity=Point2D(vx, vy))

    def move(self: Self["Robot"], count: int, width: int, height: int) -> Self["Robot"]:
        cls = type(self)
        # noinspection PyArgumentList
        return cls(
            position=Point2D(
                (self.position.x + count * self.velocity.x) % width,
                (self.position.y + count * self.velocity.y) % height,
            ),
            velocity=self.velocity,
        )


Challenge.main()
challenge = Challenge()
