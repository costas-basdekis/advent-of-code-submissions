#!/usr/bin/env python3
import string
from dataclasses import dataclass
import re
from functools import cached_property
from typing import ClassVar, Dict, List, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Point3D, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        490
        """
        return BrickStack.from_text(_input).drop_bricks().get_disintegration_count()


@dataclass
class BrickStack:
    bricks: List["Brick"]

    @classmethod
    def from_text(cls, text: str) -> "BrickStack":
        """
        >>> _stack = BrickStack.from_text('''
        ...     1,0,1~1,2,1
        ...     0,0,2~2,0,2
        ...     0,2,3~2,2,3
        ...     0,0,4~0,2,4
        ...     2,0,5~2,2,5
        ...     0,1,6~2,1,6
        ...     1,1,8~1,1,9
        ... ''')
        >>> print(_stack.get_2d_representation(0, 2))
         x
        012
        .G. 9
        .G. 8
        ... 7
        FFF 6
        ..E 5 z
        D.. 4
        CCC 3
        BBB 2
        .A. 1
        --- 0
        >>> print(_stack.get_2d_representation(1, 2))
         y
        012
        .G. 9
        .G. 8
        ... 7
        .F. 6
        EEE 5 z
        DDD 4
        ..C 3
        B.. 2
        AAA 1
        --- 0
        """
        return cls(bricks=sorted(map(Brick.from_text, text.strip().splitlines()), key=lambda brick: brick.start.z))

    brick_names = string.ascii_uppercase
    axis_names = "xyz"

    def get_2d_representation(self, first_axis_index: int, second_axis_index: int) -> str:
        min_values, max_values = self.boundaries
        min_x = min_values[first_axis_index]
        min_y = min_values[second_axis_index]
        max_x = max_values[first_axis_index]
        max_y = max_values[second_axis_index]
        bricks_by_point: Dict[Point2D, List[Brick]] = {}
        for brick in self.bricks:
            for x in range(brick.start[first_axis_index], brick.end[first_axis_index] + 1):
                for y in range(brick.start[second_axis_index], brick.end[second_axis_index] + 1):
                    point = Point2D(x, y)
                    bricks_by_point.setdefault(point, []).append(brick)
        if len(self.bricks) > len(self.brick_names):
            brick_names = {
                brick: str(index)
                for index, brick in enumerate(self.bricks, start=1)
            }
        else:
            brick_names = {
                brick: name
                for brick, name in zip(self.bricks, self.brick_names)
            }
        text_values: Dict[Point2D, str] = {
            point: (
                "."
                if not bricks else
                brick_names[bricks[0]]
                if len(bricks) == 1 else
                "?"
            )
            for x in range(min_x, max_x + 1)
            for y in range(min_y, max_y + 1)
            for point in [Point2D(x, y)]
            for bricks in [bricks_by_point.get(point, [])]
        }
        max_len = max(max(map(len, text_values.values())), max(map(len, map(str, [min_x, max_x]))))
        max_y_axis_len = max(map(len, map(str, [min_y, max_y])))
        x_separator = " " if max_len > 1 else ""
        return "{}\n{}\n{}\n{}".format(
            self.axis_names[first_axis_index].center(max_x - min_x + 1),
            x_separator.join(str(x).center(max_len) for x in range(min_x, max_x + 1)),
            "\n".join(
                "{} {} {}".format(
                    x_separator.join(
                        text_values[point]
                        for x in range(min_x, max_x + 1)
                        for point in [Point2D(x, y)]
                    ),
                    str(y).rjust(max_y_axis_len),
                    self.axis_names[second_axis_index]
                    if y == (max_y + 1) // 2 else
                    "",
                )
                for y in range(max_y, 1 - 1, -1)
            ),
            "{} {}".format(
                "-" * (max_x - min_x + 1),
                "0".rjust(max_y_axis_len)
            ),
        )

    @cached_property
    def boundaries(self) -> Tuple[Point3D, Point3D]:
        return min_and_max_tuples(point for brick in self.bricks for point in (brick.start, brick.end))

    def drop_bricks(self) -> "BrickStack":
        """
        >>> _stack = BrickStack.from_text('''
        ...     1,0,1~1,2,1
        ...     0,0,2~2,0,2
        ...     0,2,3~2,2,3
        ...     0,0,4~0,2,4
        ...     2,0,5~2,2,5
        ...     0,1,6~2,1,6
        ...     1,1,8~1,1,9
        ... ''')
        >>> _dropped = _stack.drop_bricks()
        >>> print(_dropped.get_2d_representation(0, 2))
         x
        012
        .G. 6
        .G. 5
        FFF 4
        D.E 3 z
        ??? 2
        .A. 1
        --- 0
        >>> print(_dropped.get_2d_representation(1, 2))
         y
        012
        .G. 6
        .G. 5
        .F. 4
        ??? 3 z
        B.C 2
        AAA 1
        --- 0
        """
        min_values, max_values = self.boundaries
        current_height: Dict[Point2D, int] = {
            Point2D(x, y): 0
            for x in range(min_values.x, max_values.x + 1)
            for y in range(min_values.y, max_values.y + 1)
        }
        output_bricks = []
        for brick in self.bricks:
            max_height = max(
                current_height[Point2D(x, y)]
                for x in range(brick.start.x, brick.end.x + 1)
                for y in range(brick.start.y, brick.end.y + 1)
            )
            z_offset = brick.start.z - max_height - 1
            if z_offset < 0:
                partial_current_height = {
                    Point2D(x, y): current_height[Point2D(x, y)]
                    for x in range(brick.start.x, brick.end.x + 1)
                    for y in range(brick.start.y, brick.end.y + 1)
                }
                raise Exception(f"Brick #{self.bricks.index(brick)} {brick} is intersecting with previous bricks {partial_current_height}")
            elif z_offset > 0:
                output_brick = brick.offset(Point3D(0, 0, -z_offset))
            else:
                output_brick = brick
            current_height.update({
                Point2D(x, y): output_brick.end.z
                for x in range(output_brick.start.x, output_brick.end.x + 1)
                for y in range(output_brick.start.y, output_brick.end.y + 1)
            })
            output_bricks.append(output_brick)
        return BrickStack(bricks=output_bricks)

    def get_disintegration_count(self) -> int:
        """
        >>> _stack = BrickStack.from_text('''
        ...     1,0,1~1,2,1
        ...     0,0,2~2,0,2
        ...     0,2,3~2,2,3
        ...     0,0,4~0,2,4
        ...     2,0,5~2,2,5
        ...     0,1,6~2,1,6
        ...     1,1,8~1,1,9
        ... ''').drop_bricks()
        >>> _stack.get_disintegration_count()
        5
        """
        return sum(
            1
            for dependencies in self.get_brick_disintegration_dependencies().values()
            if not dependencies
        )

    def get_brick_disintegration_dependencies(self) -> Dict["Brick", Set["Brick"]]:
        """
        >>> def _check(s: BrickStack):
        ...     ds = s.get_brick_disintegration_dependencies()
        ...     print("\\n".join(
        ...         f"{s.brick_names[s.bricks.index(_brick)]}: {', '.join(sorted(s.brick_names[s.bricks.index(d)] for d in ds[_brick]))}"
        ...         for _brick in s.bricks
        ...     ))
        >>> _stack = BrickStack.from_text('''
        ...     1,0,1~1,2,1
        ...     0,0,2~2,0,2
        ...     0,2,3~2,2,3
        ...     0,0,4~0,2,4
        ...     2,0,5~2,2,5
        ...     0,1,6~2,1,6
        ...     1,1,8~1,1,9
        ... ''').drop_bricks()
        >>> _check(_stack)
        A: B, C
        B:
        C:
        D:
        E:
        F: G
        G:
        """
        dependencies = self.get_brick_dependencies()
        reverse_dependencies: Dict[Brick, Set[Brick]] = {
            brick: set()
            for brick in self.bricks
        }
        for brick, brick_dependencies in dependencies.items():
            for dependency in brick_dependencies:
                reverse_dependencies[dependency].add(brick)
        disintegration_dependencies: Dict[Brick, Set[Brick]] = {
            brick: set()
            for brick in self.bricks
        }
        for brick, brick_dependencies in reverse_dependencies.items():
            for dependency in brick_dependencies:
                # print(f"Checking for {self.bricks.index(brick)} dependency {self.bricks.index(dependency)} which has dependencies of {[self.bricks.index(b) for b in dependencies[dependency]]}: {(dependencies[dependency] == {brick})}")
                if dependencies[dependency] == {brick}:
                    disintegration_dependencies[brick].add(dependency)
        return disintegration_dependencies

    def get_brick_dependencies(self) -> Dict["Brick", Set["Brick"]]:
        """
        >>> def _check(s: BrickStack):
        ...     ds = s.get_brick_dependencies()
        ...     print("\\n".join(
        ...         f"{s.brick_names[s.bricks.index(_brick)]}: {', '.join(sorted(s.brick_names[s.bricks.index(d)] for d in ds.get(_brick, set())))}"
        ...         for _brick in s.bricks
        ...     ))
        >>> _stack = BrickStack.from_text('''
        ...     1,0,1~1,2,1
        ...     0,0,2~2,0,2
        ...     0,2,3~2,2,3
        ...     0,0,4~0,2,4
        ...     2,0,5~2,2,5
        ...     0,1,6~2,1,6
        ...     1,1,8~1,1,9
        ... ''').drop_bricks()
        >>> _check(_stack)
        A:
        B: A
        C: A
        D: B, C
        E: B, C
        F: D, E
        G: F
        """
        brick_at_position: Dict[Point3D, Brick] = {}
        dependencies: Dict[Brick, Set[Brick]] = {}
        # print(f"Before {self.bricks.index(self.bricks[0])}: {({p: self.bricks.index(b) for p, b in brick_at_position.items()})}")
        for brick in self.bricks:
            dependencies[brick] = {
                brick_at_position.get(Point3D(x, y, brick.start.z - 1))
                for x in range(brick.start.x, brick.end.x + 1)
                for y in range(brick.start.y, brick.end.y + 1)
            } - {None}
            # print(f"Dependencies of {self.bricks.index(brick)} ({brick}): {[self.bricks.index(b) for b in dependencies[brick]]}")
            brick_at_position.update({
                Point3D(x, y, brick.end.z): brick
                for x in range(brick.start.x, brick.end.x + 1)
                for y in range(brick.start.y, brick.end.y + 1)
            })
            # print(f"After {self.bricks.index(brick)}: {({p: self.bricks.index(b) for p, b in brick_at_position.items()})}")
        return dependencies


@dataclass(unsafe_hash=True, order=True)
class Brick:
    start: Point3D
    end: Point3D

    re_brick: ClassVar[re.Pattern] = re.compile(r'^(-?\d+),(-?\d+),(-?\d+)~(-?\d+),(-?\d+),(-?\d+)$')

    @classmethod
    def from_text(cls, text: str) -> "Brick":
        """
        >>> print(Brick.from_text('''1,0,1~1,2,1'''))
        1,0,1~1,2,1
        >>> print(Brick.from_text('''1,2,1~1,0,1'''))
        1,0,1~1,2,1
        """
        x1_str, y1_str, z1_str, x2_str, y2_str, z2_str = cls.re_brick.match(text.strip()).groups()
        x1, y1, z1, x2, y2, z2 = map(int, [x1_str, y1_str, z1_str, x2_str, y2_str, z2_str])
        x_start, x_end = sorted([x1, x2])
        y_start, y_end = sorted([y1, y2])
        z_start, z_end = sorted([z1, z2])
        return cls(start=Point3D(x_start, y_start, z_start), end=Point3D(x_end, y_end, z_end))

    def __str__(self) -> str:
        return f"{self.start.x},{self.start.y},{self.start.z}~{self.end.x},{self.end.y},{self.end.z}"

    def offset(self, offset: Point3D) -> "Brick":
        return Brick(start=self.start.offset(offset), end=self.end.offset(offset))


Challenge.main()
challenge = Challenge()
