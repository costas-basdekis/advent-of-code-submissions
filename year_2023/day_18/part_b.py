#!/usr/bin/env python3
import itertools
from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar, Dict, Union, List, Tuple, Iterable, Optional

import click

from aox.challenge import Debugger
from utils import BaseChallenge, Direction, Point2D, sign, min_and_max_tuples
from year_2023.day_18 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        129849166997110
        """
        return DigInstructionSetExtended.from_instructions_text(_input).fix().get_total_area(debugger=debugger)

    def play(self):
        import pathlib
        initial_path = DigInstructionSetExtended.from_instructions_text(pathlib.Path(__file__).parent.joinpath('input.txt').read_text()).to_path()
        actual_area = 40714
        iteration_index = -1
        paths = []
        while True:
            input_text = click.prompt("How many iterations? (-1 for no limit, p for debug, o for output)")
            if input_text == "p":
                import ipdb; ipdb.set_trace()
                continue
            if input_text == "o":
                if iteration_index == -1:
                    print("Nothing to output, run once first")
                    continue
                pathlib.Path(__file__).parent.joinpath(f'squashed_output_{iteration_index}.txt').write_text(str(Path.paths_to_lagoon(paths)))
                print(f"wrote to squashed_output_{iteration_index}.txt")
                continue
            if input_text == "":
                input_text = "-1"
            iteration_count = int(input_text)
            if iteration_count >= 0:
                iterations = range(1, iteration_count + 1)
            else:
                iterations = itertools.count()
            paths = [initial_path]
            squashed_area = 0
            iteration_index = 0
            for iteration_index in iterations:
                if not paths:
                    break
                path = paths.pop(0)
                area, new_paths = path.squash_top_line()
                squashed_area += area
                paths.extend(new_paths)
            remaining_area = sum((
                path.to_lagoon().extend_with_internal().hole_count
                for path in paths
            ), 0)
            total_area = squashed_area + remaining_area
            print(
                f"Squashed {squashed_area} after {iteration_index} iterations, "
                f"remaining {remaining_area}, "
                f"totaling {total_area} {'==' if total_area == actual_area else '!='} {actual_area}"
            )


@dataclass
class Line:
    start: Point2D
    end: Point2D

    def overlaps_with(self, other: "Line") -> bool:
        """
        >>> Line(Point2D(0, 0), Point2D(0, 10)).overlaps_with(Line(Point2D(2, 0), Point2D(2, 10)))
        False
        >>> Line(Point2D(0, 0), Point2D(0, 10)).overlaps_with(Line(Point2D(0, 0), Point2D(0, 10)))
        True
        >>> Line(Point2D(0, 0), Point2D(0, 10)).overlaps_with(Line(Point2D(0, 5), Point2D(0, 15)))
        True
        >>> Line(Point2D(0, 0), Point2D(0, 10)).overlaps_with(Line(Point2D(0, -5), Point2D(0, 5)))
        True
        >>> Line(Point2D(0, 0), Point2D(0, 10)).overlaps_with(Line(Point2D(0, -5), Point2D(0, 15)))
        True
        >>> Line(Point2D(0, 0), Point2D(0, 10)).overlaps_with(Line(Point2D(0, 3), Point2D(0, 7)))
        True
        >>> Line(Point2D(0, 0), Point2D(0, 10)).overlaps_with(Line(Point2D(0, 10), Point2D(0, 20)))
        False
        >>> Line(Point2D(0, 0), Point2D(0, 10)).overlaps_with(Line(Point2D(0, -10), Point2D(0, 0)))
        False
        >>> Line(Point2D(0, 0), Point2D(0, 10)).overlaps_with(Line(Point2D(0, 15), Point2D(0, 25)))
        False
        >>> Line(Point2D(0, 0), Point2D(10, 0)).overlaps_with(Line(Point2D(0, 2), Point2D(10, 2)))
        False
        >>> Line(Point2D(0, 0), Point2D(10, 0)).overlaps_with(Line(Point2D(0, 0), Point2D(10, 0)))
        True
        >>> Line(Point2D(0, 0), Point2D(10, 0)).overlaps_with(Line(Point2D(5, 0), Point2D(15, 0)))
        True
        >>> Line(Point2D(0, 0), Point2D(10, 0)).overlaps_with(Line(Point2D(-5, 0), Point2D(5, 0)))
        True
        >>> Line(Point2D(0, 0), Point2D(10, 0)).overlaps_with(Line(Point2D(-5, 0), Point2D(15, 0)))
        True
        >>> Line(Point2D(0, 0), Point2D(10, 0)).overlaps_with(Line(Point2D(3, 0), Point2D(7, 0)))
        True
        >>> Line(Point2D(0, 0), Point2D(10, 0)).overlaps_with(Line(Point2D(10, 0), Point2D(20, 0)))
        False
        >>> Line(Point2D(0, 0), Point2D(10, 0)).overlaps_with(Line(Point2D(-10, 0), Point2D(0, 0)))
        False
        >>> Line(Point2D(0, 0), Point2D(10, 0)).overlaps_with(Line(Point2D(15, 0), Point2D(25, 0)))
        False
        """
        if self.is_horizontal():
            if other.is_horizontal():
                if self.start.y != other.start.y:
                    return False
                return (
                    self.is_x_inside(other.start.x)
                    or self.is_x_inside(other.end.x)
                    or other.is_x_inside(self.start.x)
                    or other.is_x_inside(self.end.x)
                    or (
                        self.is_x_inside_inclusive(other.start.x)
                        and self.is_x_inside_inclusive(other.end.x)
                    )
                )
            else:
                return (
                    self.is_x_inside(other.start.x)
                    and other.is_y_inside(self.start.y)
                )
        else:
            if other.is_horizontal():
                return (
                    self.is_y_inside(other.start.y)
                    and other.is_x_inside(self.start.x)
                )
            else:
                if self.start.x != other.start.x:
                    return False
                return (
                    self.is_y_inside(other.start.y)
                    or self.is_y_inside(other.end.y)
                    or other.is_y_inside(self.start.y)
                    or other.is_y_inside(self.end.y)
                    or (
                        self.is_y_inside_inclusive(other.start.y)
                        and self.is_y_inside_inclusive(other.end.y)
                    )
                )

    def is_horizontal(self) -> bool:
        return self.start.y == self.end.y

    def is_empty(self) -> bool:
        return self.start == self.end

    def is_x_inside(self, x: float) -> bool:
        """
        >>> [Line(Point2D(0, 0), Point2D(10, 0)).is_x_inside(x) for x in [-1, 0, 5, 10, 11]]
        [False, False, True, False, False]
        >>> [Line(Point2D(10, 0), Point2D(0, 0)).is_x_inside(x) for x in [-1, 0, 5, 10, 11]]
        [False, False, True, False, False]
        >>> [Line(Point2D(0, 0), Point2D(0, 10)).is_x_inside(x) for x in [-1, 0, 5, 10, 11]]
        [False, False, False, False, False]
        >>> [Line(Point2D(0, 10), Point2D(0, 0)).is_x_inside(x) for x in [-1, 0, 5, 10, 11]]
        [False, False, False, False, False]
        """
        x1 = self.start.x
        x2 = self.end.x
        if x2 < x1:
            x1, x2 = x2, x1
        return x1 < x < x2

    def is_x_inside_inclusive(self, x: float) -> bool:
        """
        >>> [Line(Point2D(0, 0), Point2D(10, 0)).is_x_inside_inclusive(x) for x in [-1, 0, 5, 10, 11]]
        [False, True, True, True, False]
        >>> [Line(Point2D(10, 0), Point2D(0, 0)).is_x_inside_inclusive(x) for x in [-1, 0, 5, 10, 11]]
        [False, True, True, True, False]
        >>> [Line(Point2D(0, 0), Point2D(0, 10)).is_x_inside_inclusive(x) for x in [-1, 0, 5, 10, 11]]
        [False, True, False, False, False]
        >>> [Line(Point2D(0, 10), Point2D(0, 0)).is_x_inside_inclusive(x) for x in [-1, 0, 5, 10, 11]]
        [False, True, False, False, False]
        """
        x1 = self.start.x
        x2 = self.end.x
        if x2 < x1:
            x1, x2 = x2, x1
        return x1 <= x <= x2

    def is_y_inside(self, y: float) -> bool:
        """
        >>> [Line(Point2D(0, 0), Point2D(0, 10)).is_y_inside(y) for y in [-1, 0, 5, 10, 11]]
        [False, False, True, False, False]
        >>> [Line(Point2D(0, 10), Point2D(0, 0)).is_y_inside(y) for y in [-1, 0, 5, 10, 11]]
        [False, False, True, False, False]
        >>> [Line(Point2D(0, 0), Point2D(10, 0)).is_y_inside(y) for y in [-1, 0, 5, 10, 11]]
        [False, False, False, False, False]
        >>> [Line(Point2D(10, 0), Point2D(0, 0)).is_y_inside(y) for y in [-1, 0, 5, 10, 11]]
        [False, False, False, False, False]
        """
        y1 = self.start.y
        y2 = self.end.y
        if y2 < y1:
            y1, y2 = y2, y1
        return y1 < y < y2

    def is_y_inside_inclusive(self, y: float) -> bool:
        """
        >>> [Line(Point2D(0, 0), Point2D(0, 10)).is_y_inside_inclusive(y) for y in [-1, 0, 5, 10, 11]]
        [False, True, True, True, False]
        >>> [Line(Point2D(0, 10), Point2D(0, 0)).is_y_inside_inclusive(y) for y in [-1, 0, 5, 10, 11]]
        [False, True, True, True, False]
        >>> [Line(Point2D(0, 0), Point2D(10, 0)).is_y_inside_inclusive(y) for y in [-1, 0, 5, 10, 11]]
        [False, True, False, False, False]
        >>> [Line(Point2D(10, 0), Point2D(0, 0)).is_y_inside_inclusive(y) for y in [-1, 0, 5, 10, 11]]
        [False, True, False, False, False]
        """
        y1 = self.start.y
        y2 = self.end.y
        if y2 < y1:
            y1, y2 = y2, y1
        return y1 <= y <= y2

    def offset(self, offset: Point2D, factor: float = 1) -> "Line":
        return Line(
            start=self.start.offset(offset, factor=factor),
            end=self.end.offset(offset, factor=factor),
        )

    def get_boundary_points(self) -> Iterable[Point2D]:
        if self.is_horizontal():
            if self.start.x <= self.end.x:
                xs = range(self.start.x, self.end.x + 1)
            else:
                xs = range(self.end.x, self.start.x + 1)
            ys = [self.start.y]
        else:
            if self.start.y <= self.end.y:
                ys = range(self.start.y, self.end.y + 1)
            else:
                ys = range(self.end.y, self.start.y + 1)
            xs = [self.start.x]
        return (
            Point2D(x, y)
            for x in xs
            for y in ys
        )

    def get_x_sign(self) -> int:
        return sign(self.end.x - self.start.x)

    def get_y_sign(self) -> int:
        return sign(self.end.y - self.start.y)

    def get_direction(self) -> Direction:
        return Direction.from_offset(Point2D(self.get_x_sign(), self.get_y_sign()))


@dataclass
class Path:
    lines: List[Line]

    @classmethod
    def from_instruction_set(cls, instruction_set: "DigInstructionSetExtended") -> "Path":
        """
        >>> print(Path.from_instruction_set(DigInstructionSetExtended.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''')))
        #######
        #.....#
        ###...#
        ..#...#
        ..#...#
        ###.###
        #...#..
        ##..###
        .#....#
        .######
        """
        position = Point2D(0, 0)
        thick_points: List[Point2D] = [position]
        for instruction in instruction_set.instructions:
            position = position.offset(instruction.get_offset())
            thick_points.append(position)
        if thick_points[-1] != thick_points[0]:
            raise Exception(f"Start {thick_points[0]} and end {thick_points[-1]} don't match")
        return Path.from_thick_points(thick_points[:-1])

    @classmethod
    def from_thick_points(cls, thick_points: List[Point2D]) -> "Path":
        return cls.from_thick_lines(cls.thick_points_to_thick_lines(thick_points))

    @classmethod
    def thick_points_to_thick_lines(cls, thick_points: List[Point2D]) -> List[Line]:
        return [
            Line(first, second)
            for first, second
            in zip(thick_points, thick_points[1:] + thick_points[:1])
        ]

    clockwise_outer_offset_map: ClassVar[Dict[Direction, Point2D]] = {
        Direction.Down: Direction.Right.offset,
        Direction.Up: Point2D(0, 0),
        Direction.Left: Direction.Down.offset,
        Direction.Right: Point2D(0, 0),
    }

    counterclockwise_outer_offset_map: ClassVar[Dict[Direction, Point2D]] = {
        Direction.Down: Point2D(0, 0),
        Direction.Up: Direction.Right.offset,
        Direction.Left: Point2D(0, 0),
        Direction.Right: Direction.Down.offset,
    }

    @classmethod
    def from_thick_lines(cls, thick_lines: List[Line]) -> "Path":
        return cls.from_lines(cls.thick_lines_to_lines(thick_lines))

    @classmethod
    def thick_lines_to_lines(cls, thick_lines: List[Line]) -> List[Line]:
        """
        >>> def check(_thick_points: List[Point2D]) -> List[Line]:
        ...     _thick_lines = Path.thick_points_to_thick_lines(_thick_points)
        ...     return Path.thick_lines_to_lines(_thick_lines)
        >>> check([Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)])
        [Line(start=Point2D(x=0, y=0), end=Point2D(x=3, y=0)),
            Line(start=Point2D(x=3, y=0), end=Point2D(x=3, y=3)),
            Line(start=Point2D(x=3, y=3), end=Point2D(x=0, y=3)),
            Line(start=Point2D(x=0, y=3), end=Point2D(x=0, y=0))]
        >>> check([Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(2, 4), Point2D(2, 2),
        ...     Point2D(0, 2)])
        [Line(start=Point2D(x=0, y=0), end=Point2D(x=5, y=0)),
            Line(start=Point2D(x=5, y=0), end=Point2D(x=5, y=5)),
            Line(start=Point2D(x=5, y=5), end=Point2D(x=2, y=5)),
            Line(start=Point2D(x=2, y=5), end=Point2D(x=2, y=3)),
            Line(start=Point2D(x=2, y=3), end=Point2D(x=0, y=3)),
            Line(start=Point2D(x=0, y=3), end=Point2D(x=0, y=0))]
        """
        if not thick_lines:
            return []
        a_top_line = min(thick_lines, key=lambda line: line.start.y)
        if a_top_line.get_x_sign() > 0:
            offset_map = cls.clockwise_outer_offset_map
        else:
            offset_map = cls.counterclockwise_outer_offset_map
        lines = [
            thick_line.offset(offset_map[thick_line.get_direction()])
            for thick_line
            in thick_lines
        ]
        lines = [
            Line(Point2D(prev_line.end.x, line.start.y), Point2D(next_line.start.x, line.end.y))
            if line.is_horizontal() else
            Line(Point2D(line.start.x, prev_line.end.y), Point2D(line.end.x, next_line.start.y))
            for prev_line, line, next_line
            in zip(lines[-1:] + lines[:-1], lines, lines[1:] + lines[:1])
        ]
        return lines

    @classmethod
    def lines_to_thick_lines(cls, lines: List[Line]) -> List[Line]:
        """
        >>> Path.lines_to_thick_lines([Line(start=Point2D(x=0, y=0), end=Point2D(x=3, y=0)),
        ...     Line(start=Point2D(x=3, y=0), end=Point2D(x=3, y=3)),
        ...     Line(start=Point2D(x=3, y=3), end=Point2D(x=0, y=3)),
        ...     Line(start=Point2D(x=0, y=3), end=Point2D(x=0, y=0))])
        [Line(start=Point2D(x=0, y=0), end=Point2D(x=2, y=0)),
            Line(start=Point2D(x=2, y=0), end=Point2D(x=2, y=2)),
            Line(start=Point2D(x=2, y=2), end=Point2D(x=0, y=2)),
            Line(start=Point2D(x=0, y=2), end=Point2D(x=0, y=0))]
        """
        if not lines:
            return []
        a_top_line = min(lines, key=lambda line: line.start.y)
        if a_top_line.get_x_sign() > 0:
            offset_map = cls.clockwise_outer_offset_map
        else:
            offset_map = cls.counterclockwise_outer_offset_map
        thick_lines = [
            line.offset(offset_map[line.get_direction()], factor=-1)
            for line
            in lines
        ]
        thick_lines = [
            Line(Point2D(prev_line.end.x, line.start.y), Point2D(next_line.start.x, line.end.y))
            if line.is_horizontal() else
            Line(Point2D(line.start.x, prev_line.end.y), Point2D(line.end.x, next_line.start.y))
            for prev_line, line, next_line
            in zip(thick_lines[-1:] + thick_lines[:-1], thick_lines, thick_lines[1:] + thick_lines[:1])
        ]
        return thick_lines

    @classmethod
    def from_lines(cls, lines: List[Line]) -> "Path":
        cls.check_lines(lines)
        return cls(lines=lines)

    @classmethod
    def check_lines(cls, lines: List[Line]):
        for first_index in range(len(lines)):
            first_line = lines[first_index]
            first_is_horizontal = first_line.is_horizontal()
            second_line = lines[(first_index + 1) % len(lines)]
            if (first_line.get_x_sign() == 0) == (first_line.get_y_sign() == 0):
                raise Exception(f"Line is not orthogonal: {first_line}\n{Path(lines=lines)}")
            if first_is_horizontal == second_line.is_horizontal():
                try:
                    path_str = str(Path(lines=lines))
                except Exception as e:
                    print(e)
                    path_str = repr(Path(lines=lines))
                raise Exception(f"Consecutive lines are not perpendicular: {first_line} and {second_line}:\n{path_str}")
            if first_line.end != second_line.start:
                raise Exception(f"Consecutive lines are not starting and ending on the same point: {first_line} and {second_line}:\n{Path(lines=lines)}")

    @classmethod
    def paths_to_lagoon(cls, paths: List["Path"]) -> part_a.Lagoon:
        holes = set()
        for path in paths:
            holes.update(path.to_lagoon().holes)
        return part_a.Lagoon(holes=holes)

    def __str__(self) -> str:
        return str(self.to_lagoon())

    def __getitem__(self, index: int) -> Line:
        return self.lines[self.normalise_index(index)]

    def normalise_index(self, index: int) -> int:
        return index % len(self.lines)

    @cached_property
    def boundaries(self) -> Tuple[Point2D, Point2D]:
        return min_and_max_tuples(
            point
            for line in self.lines
            for point in [line.start, line.end]
        )

    def to_lagoon(self) -> part_a.Lagoon:
        """
        >>> print(Path.from_thick_points([Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]).to_lagoon())
        ###
        #.#
        ###
        """
        return part_a.Lagoon({
            point
            for line in self.lines_to_thick_lines(self.lines)
            for point in line.get_boundary_points()
        })

    def squash(self, debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> _path = DigInstructionSetExtended.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''').to_path()
        >>> print(_path)
        #######
        #.....#
        ###...#
        ..#...#
        ..#...#
        ###.###
        #...#..
        ##..###
        .#....#
        .######
        >>> _path.squash()
        62
        """
        paths = [self]
        total_area = 0
        while debugger.step_if(paths):
            path = paths.pop(0)
            area, new_paths = path.squash_top_line()
            total_area += area
            paths.extend(new_paths)
            if debugger.should_report():
                debugger.default_report_if(f"Cleared {total_area}, {sum(len(path.lines) for path in paths)} lines in {len(paths)} paths")
        return total_area

    def squash_top_line(self) -> Tuple[int, List["Path"]]:
        """
        >>> _path = DigInstructionSetExtended.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''').to_path()
        >>> print(_path)
        #######
        #.....#
        ###...#
        ..#...#
        ..#...#
        ###.###
        #...#..
        ##..###
        .#....#
        .######
        >>> area, _paths = _path.squash_top_line()
        >>> area
        21
        >>> print("\\n-\\n".join(sorted(map(str, _paths))))
        ..#####
        ..#...#
        ###.###
        #...#..
        ##..###
        .#....#
        .######
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 2), Point2D(4, 2), Point2D(4, 4),
        ...     Point2D(2, 4), Point2D(2, 2), Point2D(0, 2)])
        >>> print(_path)
        #######
        #.....#
        ###.###
        ..#.#..
        ..###..
        >>> area, _paths = _path.squash_top_line()
        >>> area
        21
        >>> print("\\n-\\n".join(sorted(map(str, _paths))))
        ###
        ###
        >>> _path = Path.from_thick_points([Point2D(2, 0), Point2D(4, 0), Point2D(4, 2), Point2D(6, 2), Point2D(6, 4),
        ...     Point2D(0, 4), Point2D(0, 2), Point2D(2, 2)])
        >>> print(_path)
        ..###..
        ..#.#..
        ###.###
        #.....#
        #######
        >>> area, _paths = _path.squash_top_line()
        >>> area
        6
        >>> print("\\n-\\n".join(sorted(map(str, _paths))))
        #######
        #.....#
        #######
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 3), Point2D(4, 3), Point2D(4, 4),
        ...     Point2D(2, 4), Point2D(2, 2), Point2D(0, 2)])
        >>> print(_path)
        #######
        #.....#
        ###...#
        ..#.###
        ..###..
        >>> area, _paths = _path.squash_top_line()
        >>> area
        21
        >>> print("\\n-\\n".join(sorted(map(str, _paths))))
        #####
        ###..
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 2), Point2D(4, 2), Point2D(4, 4),
        ...     Point2D(2, 4), Point2D(2, 3), Point2D(0, 3)])
        >>> print(_path)
        #######
        #.....#
        #...###
        ###.#..
        ..###..
        >>> area, _paths = _path.squash_top_line()
        >>> area
        21
        >>> print("\\n-\\n".join(sorted(map(str, _paths))))
        #####
        ..###
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 3), Point2D(4, 3), Point2D(4, 2),
        ...     Point2D(2, 2), Point2D(2, 4), Point2D(0, 4)])
        >>> print(_path)
        #######
        #.....#
        #.###.#
        #.#.###
        ###....
        >>> print("\\n-\\n".join(sorted(map(str, _path.squash_top_line()[1]))))
        ###
        -
        ###
        ###
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(10, 0), Point2D(10, 4), Point2D(8, 4), Point2D(8, 2),
        ...     Point2D(6, 2), Point2D(6, 3), Point2D(4, 3), Point2D(4, 2), Point2D(2, 2), Point2D(2, 4),
        ...     Point2D(0, 4)])
        >>> print(_path)
        ###########
        #.........#
        #.###.###.#
        #.#.###.#.#
        ###.....###
        >>> area, _paths = _path.squash_top_line()
        >>> area
        33
        >>> print("\\n-\\n".join(sorted(map(str, _paths))))
        ###
        -
        ###
        ###
        -
        ###
        ###
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(14, 0), Point2D(14, 3), Point2D(12, 3), Point2D(12, 2),
        ...     Point2D(10, 2), Point2D(10, 4), Point2D(8, 4), Point2D(8, 2), Point2D(6, 2), Point2D(6, 3),
        ...     Point2D(4, 3), Point2D(4, 2), Point2D(2, 2), Point2D(2, 4), Point2D(0, 4)])
        >>> print(_path)
        ###############
        #.............#
        #.###.###.###.#
        #.#.###.#.#.###
        ###.....###....
        >>> area, _paths = _path.squash_top_line()
        >>> area
        45
        >>> print("\\n-\\n".join(sorted(map(str, _paths))))
        ###
        -
        ###
        -
        ###
        ###
        -
        ###
        ###
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(7, 0), Point2D(7, 3), Point2D(5, 3), Point2D(5, 2),
        ...     Point2D(3, 2), Point2D(3, 4), Point2D(1, 4), Point2D(1, 2), Point2D(0, 2)])
        >>> print(_path)
        ########
        #......#
        ##.###.#
        .#.#.###
        .###....
        >>> area, _paths = _path.squash_top_line()
        >>> area
        24
        >>> print("\\n-\\n".join(sorted(map(str, _paths))))
        ###
        -
        ###
        ###
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 2), Point2D(0, 2)])
        >>> print(_path)
        #######
        #.....#
        #######
        >>> area, _paths = _path.squash_top_line()
        >>> area
        21
        >>> _paths
        []
        """
        top_line_to_squash = self.get_top_line_to_squash()
        if not top_line_to_squash:
            return 0, []
        line, new_y, overlaps = top_line_to_squash
        return self.get_squashed_area(line, new_y), self.squash_line(line, new_y, overlaps)

    def get_squashed_area(self, line: Line, new_y: int) -> int:
        return abs(line.end.x - line.start.x) * (new_y - line.start.y)

    def get_top_line_to_squash(self) -> Optional[Tuple[Line, int, List[Line]]]:
        """
        >>> _path = Path.from_instruction_set(DigInstructionSetExtended.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... '''))
        >>> print(_path)
        #######
        #.....#
        ###...#
        ..#...#
        ..#...#
        ###.###
        #...#..
        ##..###
        .#....#
        .######
        >>> _path.get_top_line_to_squash()
        (Line(start=Point2D(x=0, y=0), end=Point2D(x=7, y=0)), 3, [])
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 2), Point2D(4, 2), Point2D(4, 4),
        ...     Point2D(2, 4), Point2D(2, 2), Point2D(0, 2)])
        >>> print(_path)
        #######
        #.....#
        ###.###
        ..#.#..
        ..###..
        >>> _path.get_top_line_to_squash()
        (Line(start=Point2D(x=0, y=0), end=Point2D(x=7, y=0)), 3, [])
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 3), Point2D(4, 3), Point2D(4, 5),
        ...     Point2D(0, 5)])
        >>> print(_path)
        #######
        #.....#
        #.....#
        #...###
        #...#..
        #####..
        >>> _path.get_top_line_to_squash()
        (Line(start=Point2D(x=0, y=0), end=Point2D(x=7, y=0)), 4, [])
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(2, 0), Point2D(2, 3), Point2D(4, 3), Point2D(4, 0),
        ...     Point2D(7, 0), Point2D(7, 2), Point2D(6, 2), Point2D(6, 5), Point2D(0, 5)])
        >>> print(_path)
        ###.####
        #.#.#..#
        #.#.#.##
        #.###.#.
        #.....#.
        #######.
        >>> _path.get_top_line_to_squash()
        (Line(start=Point2D(x=0, y=0), end=Point2D(x=3, y=0)), 3, [])
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(7, 0), Point2D(7, 3), Point2D(5, 3), Point2D(5, 2),
        ...     Point2D(3, 2), Point2D(3, 4), Point2D(1, 4), Point2D(1, 2), Point2D(0, 2)])
        >>> print(_path)
        ########
        #......#
        ##.###.#
        .#.#.###
        .###....
        >>> _path.get_top_line_to_squash()
        (Line(start=Point2D(x=0, y=0), end=Point2D(x=8, y=0)), 3, [Line(start=Point2D(x=5, y=3), end=Point2D(x=4, y=3))])
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(7, 0), Point2D(7, 3), Point2D(9, 3), Point2D(9, 1),
        ...     Point2D(11, 1), Point2D(11, 5), Point2D(5, 5), Point2D(5, 2), Point2D(3, 2), Point2D(3, 4),
        ...     Point2D(1, 4), Point2D(1, 2), Point2D(0, 2)])
        >>> print(_path)
        ########....
        #......#.###
        ##.###.#.#.#
        .#.#.#.###.#
        .###.#.....#
        .....#######
        >>> _path.get_top_line_to_squash()
        (Line(start=Point2D(x=0, y=0), end=Point2D(x=8, y=0)), 3, [Line(start=Point2D(x=5, y=3), end=Point2D(x=4, y=3))])
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 3), Point2D(4, 3), Point2D(4, 2),
        ...     Point2D(2, 2), Point2D(2, 5), Point2D(0, 5)])
        >>> print(_path)
        #######
        #.....#
        #.###.#
        #.#.###
        #.#....
        ###....
        >>> _path.get_top_line_to_squash()
        (Line(start=Point2D(x=0, y=0), end=Point2D(x=7, y=0)), 3, [Line(start=Point2D(x=4, y=3), end=Point2D(x=3, y=3))])
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 3), Point2D(4, 3), Point2D(4, 4),
        ...     Point2D(2, 4), Point2D(2, 2), Point2D(0, 2)])
        >>> print(_path)
        #######
        #.....#
        ###...#
        ..#.###
        ..###..
        >>> _path.get_top_line_to_squash()
        (Line(start=Point2D(x=0, y=0), end=Point2D(x=7, y=0)), 3, [])
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 2), Point2D(4, 2), Point2D(4, 4),
        ...     Point2D(2, 4), Point2D(2, 3), Point2D(0, 3)])
        >>> print(_path)
        #######
        #.....#
        #...###
        ###.#..
        ..###..
        >>> _path.get_top_line_to_squash()
        (Line(start=Point2D(x=0, y=0), end=Point2D(x=7, y=0)), 3, [])
        >>> _path = Path.from_thick_points([Point2D(2, 0), Point2D(6, 0), Point2D(6, 2), Point2D(4, 2), Point2D(4, 4),
        ...     Point2D(0, 4), Point2D(0, 2), Point2D(2, 2)])
        >>> print(_path)
        ..#####
        ..#...#
        ###.###
        #...#..
        #####..
        >>> _path.get_top_line_to_squash()
        (Line(start=Point2D(x=2, y=0), end=Point2D(x=7, y=0)), 2, [])
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 2), Point2D(0, 2)])
        >>> print(_path)
        #######
        #.....#
        #######
        >>> _path.get_top_line_to_squash()
        (Line(start=Point2D(x=0, y=0), end=Point2D(x=7, y=0)), 3, [])
        >>> _path = Path.from_thick_points([Point2D(2, 0), Point2D(6, 0), Point2D(6, 2), Point2D(4, 2), Point2D(4, 4),
        ...     Point2D(0, 4), Point2D(0, 2), Point2D(2, 2)])
        >>> print(_path)
        ..#####
        ..#...#
        ###.###
        #...#..
        #####..
        >>> _path.get_top_line_to_squash()
        (Line(start=Point2D(x=2, y=0), end=Point2D(x=7, y=0)), 2, [])
        """
        lines_by_y = self.get_horizontal_lines_by_y()
        ys = sorted(lines_by_y)
        if len(ys) <= 1:
            return None
        first_y = ys[0]
        second_y = ys[1]
        line = lines_by_y[first_y][0]
        line_index = self.lines.index(line)
        prev_line = self[line_index - 1]
        next_line = self[line_index + 1]
        new_y = min(prev_line.start.y, next_line.end.y)
        if new_y >= second_y:
            prev_2_line = self[line_index - 2]
            next_2_line = self[line_index + 2]
            for alternative_y in ys[1:]:
                if alternative_y > new_y:
                    break
                new_line = line.offset(Point2D(0, alternative_y - line.start.y))
                overlaps = [
                    other
                    for other in lines_by_y[alternative_y]
                    if other != prev_2_line
                    and other != next_2_line
                    and other.overlaps_with(new_line)
                ]
                if overlaps:
                    new_y = alternative_y
                    break
        else:
            overlaps = []
        return line, new_y, overlaps

    def squash_line(self, line: Line, new_y: int, overlaps: List[Line]) -> List["Path"]:
        """
        >>> _path = DigInstructionSetExtended.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''').to_path()
        >>> print(_path)
        #######
        #.....#
        ###...#
        ..#...#
        ..#...#
        ###.###
        #...#..
        ##..###
        .#....#
        .######
        >>> print("\\n-\\n".join(sorted(map(str, _path.squash_line(_path.lines[0], 3, [])))))
        ..#####
        ..#...#
        ###.###
        #...#..
        ##..###
        .#....#
        .######
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 2), Point2D(4, 2), Point2D(4, 4),
        ...     Point2D(2, 4), Point2D(2, 2), Point2D(0, 2)])
        >>> print(_path)
        #######
        #.....#
        ###.###
        ..#.#..
        ..###..
        >>> print("\\n-\\n".join(sorted(map(str, _path.squash_line(_path.lines[0], 3, [])))))
        ###
        ###
        >>> _path = Path.from_thick_points([Point2D(2, 0), Point2D(4, 0), Point2D(4, 2), Point2D(6, 2), Point2D(6, 4),
        ...     Point2D(0, 4), Point2D(0, 2), Point2D(2, 2)])
        >>> print(_path)
        ..###..
        ..#.#..
        ###.###
        #.....#
        #######
        >>> print("\\n-\\n".join(sorted(map(str, _path.squash_line(_path.lines[0], 2, [])))))
        #######
        #.....#
        #######
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 3), Point2D(4, 3), Point2D(4, 4),
        ...     Point2D(2, 4), Point2D(2, 2), Point2D(0, 2)])
        >>> print(_path)
        #######
        #.....#
        ###...#
        ..#.###
        ..###..
        >>> print("\\n-\\n".join(sorted(map(str, _path.squash_line(_path.lines[0], 3, [])))))
        #####
        ###..
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 2), Point2D(4, 2), Point2D(4, 4),
        ...     Point2D(2, 4), Point2D(2, 3), Point2D(0, 3)])
        >>> print(_path)
        #######
        #.....#
        #...###
        ###.#..
        ..###..
        >>> print("\\n-\\n".join(sorted(map(str, _path.squash_line(_path.lines[0], 3, [])))))
        #####
        ..###
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(6, 0), Point2D(6, 3), Point2D(4, 3), Point2D(4, 2),
        ...     Point2D(2, 2), Point2D(2, 4), Point2D(0, 4)])
        >>> print(_path)
        #######
        #.....#
        #.###.#
        #.#.###
        ###....
        >>> print("\\n-\\n".join(sorted(map(str, _path.squash_line(_path.lines[0], 3, [_path.lines[4]])))))
        ###
        -
        ###
        ###
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(10, 0), Point2D(10, 4), Point2D(8, 4), Point2D(8, 2),
        ...     Point2D(6, 2), Point2D(6, 3), Point2D(4, 3), Point2D(4, 2), Point2D(2, 2), Point2D(2, 4),
        ...     Point2D(0, 4)])
        >>> print(_path)
        ###########
        #.........#
        #.###.###.#
        #.#.###.#.#
        ###.....###
        >>> print("\\n-\\n".join(sorted(map(str, _path.squash_line(_path.lines[0], 3, [
        ...     _path.lines[4], _path.lines[8]])))))
        ###
        -
        ###
        ###
        -
        ###
        ###
        >>> _path = Path.from_thick_points([Point2D(0, 0), Point2D(14, 0), Point2D(14, 3), Point2D(12, 3), Point2D(12, 2),
        ...     Point2D(10, 2), Point2D(10, 4), Point2D(8, 4), Point2D(8, 2), Point2D(6, 2), Point2D(6, 3),
        ...     Point2D(4, 3), Point2D(4, 2), Point2D(2, 2), Point2D(2, 4), Point2D(0, 4)])
        >>> print(_path)
        ###############
        #.............#
        #.###.###.###.#
        #.#.###.#.#.###
        ###.....###....
        >>> print("\\n-\\n".join(sorted(map(str, _path.squash_line(_path.lines[0], 3, [
        ...     _path.lines[4], _path.lines[8], _path.lines[12]])))))
        ###
        -
        ###
        -
        ###
        ###
        -
        ###
        ###
        >>> _path = Path.from_thick_points([Point2D(2, 0), Point2D(6, 0), Point2D(6, 2), Point2D(4, 2), Point2D(4, 4),
        ...     Point2D(0, 4), Point2D(0, 2), Point2D(2, 2)])
        >>> print(_path)
        ..#####
        ..#...#
        ###.###
        #...#..
        #####..
        >>> area, _paths = _path.squash_top_line()
        >>> area
        10
        >>> print("\\n-\\n".join(sorted(map(str, _paths))))
        #######
        #...#..
        #####..
        """
        line_index = self.lines.index(line)
        if overlaps:
            overlap_indexes = sorted(map(self.lines.index, overlaps))
            sub_path_index_pairs = []
            if self.normalise_index(line_index + 1) != self.normalise_index(overlap_indexes[0] - 1):
                sub_path_index_pairs += [
                    (line_index + 1, overlap_indexes[0] - 1),
                ]
            sub_path_index_pairs += [
                (overlap_index + 1, next_overlap_index - 1)
                for overlap_index, next_overlap_index in zip(overlap_indexes, overlap_indexes[1:])
            ]
            if self.normalise_index(overlap_indexes[-1] + 1) != self.normalise_index(line_index - 1):
                sub_path_index_pairs += [
                    (overlap_indexes[-1] + 1, line_index - 1),
                ]
        else:
            sub_path_index_pairs = [
                (line_index + 1, line_index - 1),
            ]
        sub_paths = [
            sub_path
            for start_index, end_index in sub_path_index_pairs
            for sub_path in [self.get_closed_range(start_index, end_index, new_y)]
            if sub_path
        ]
        return sub_paths

    def get_closed_range(self, start_index: int, end_index: int, new_y: int) -> Optional["Path"]:
        """
        >>> _path = DigInstructionSetExtended.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''').to_path()
        >>> print(_path)
        #######
        #.....#
        ###...#
        ..#...#
        ..#...#
        ###.###
        #...#..
        ##..###
        .#....#
        .######
        >>> print(_path.get_closed_range(1, -1, 3))
        ..#####
        ..#...#
        ###.###
        #...#..
        ##..###
        .#....#
        .######
        >>> print(_path.get_closed_range(1, -1, 5))
        #######
        #...#..
        ##..###
        .#....#
        .######
        >>> print(_path.get_closed_range(1, -1, 6))
        #####..
        ##..###
        .#....#
        .######
        """
        start_index = self.normalise_index(start_index)
        end_index = self.normalise_index(end_index)
        if start_index <= end_index:
            ranges = [range(start_index, end_index + 1)]
        else:
            ranges = [
                range(start_index, len(self.lines)),
                range(0, end_index + 1),
            ]
        lines = [
            self[index]
            for index_range in ranges
            for index in index_range
        ]
        if len(lines) == 1:
            return None
        while len(lines) > 1 and lines[0].end.y < new_y:
            lines.pop(0)
            lines.pop(0)
        while len(lines) > 1 and lines[-1].start.y < new_y:
            lines.pop()
            lines.pop()
        if len(lines) == 1:
            return None
        lines = [
            Line(Point2D(lines[0].start.x, new_y), lines[0].end)
        ] + lines[1:-1] + [
            Line(lines[-1].start, Point2D(lines[-1].end.x, new_y))
        ]
        if len(lines) > 1 and lines[0].is_empty():
            lines.pop(0)
            lines.pop(0)
        if len(lines) > 1 and lines[-1].is_empty():
            lines.pop()
            lines.pop()
        if len(lines) == 1:
            return None
        lines = [Line(lines[-1].end, lines[0].start)] + lines
        return Path.from_lines(lines)

    def get_horizontal_lines_by_y(self) -> Dict[int, List[Line]]:
        lines_by_y: Dict[int, List[Line]] = {}
        for line in self.lines:
            if not line.is_horizontal():
                continue
            lines_by_y.setdefault(line.start.y, []).append(line)
        return lines_by_y


class DigInstructionSetExtended(part_a.DigInstructionSet["DigInstructionExtended"]):
    def to_path(self) -> "Path":
        return Path.from_instruction_set(self)

    def fix(self) -> "DigInstructionSetExtended":
        """
        >>> print(DigInstructionSetExtended.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''').fix())
        R 461937 (#70c710)
        D 56407 (#0dc571)
        R 356671 (#5713f0)
        D 863240 (#d2c081)
        R 367720 (#59c680)
        D 266681 (#411b91)
        L 577262 (#8ceee2)
        U 829975 (#caa173)
        L 112010 (#1b58a2)
        D 829975 (#caa171)
        L 491645 (#7807d2)
        U 686074 (#a77fa3)
        L 5411 (#015232)
        U 500254 (#7a21e3)
        """
        return DigInstructionSetExtended(
            instructions=[
                instruction.fix()
                for instruction in self.instructions
            ],
        )

    def get_total_area(self, debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> DigInstructionSetExtended.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''').get_total_area()
        62
        >>> DigInstructionSetExtended.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''').fix().get_total_area()
        952408144115
        >>> import pathlib
        >>> DigInstructionSetExtended.from_instructions_text(pathlib.Path(__file__).parent.joinpath('input.txt').read_text()).get_total_area()
        40714
        """
        return self.to_path().squash(debugger=debugger)


class DigInstructionExtended(part_a.DigInstruction):
    int_direction_map: ClassVar[Dict[int, Direction]] = {
        0: Direction.Right,
        1: Direction.Down,
        2: Direction.Left,
        3: Direction.Up,
    }

    def fix(self) -> "DigInstructionExtended":
        """
        >>> DigInstructionExtended.from_instruction_text("R 6 (#70c710)").fix()
        DigInstructionExtended(direction=Direction.Right, amount=461937, colour='70c710')
        """
        amount_hex = self.colour[:5]
        int_direction = int(self.colour[5])
        return DigInstructionExtended(
            direction=self.int_direction_map[int_direction],
            amount=int(amount_hex, 16),
            colour=self.colour,
        )

    def get_offset(self) -> Point2D:
        return self.direction.offset.resize(self.amount)


Challenge.main()
challenge = Challenge()
