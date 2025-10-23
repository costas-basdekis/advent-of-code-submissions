#!/usr/bin/env python3
import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
import re
from enum import Enum
from functools import cached_property
from itertools import groupby
from pathlib import Path
from typing import (
    Any, cast, Callable, ClassVar, Dict, Generic, Iterable, List, Optional, Set,
    Tuple, Type, Union, TypeVar,
)

import click

from aox.challenge import Debugger
from aox.styling.shortcuts import e_error, e_success
from utils import (
    BaseIcpcChallenge, Point2D, get_type_argument_class, helper, Cls, Self, Point3D, restart_process,
)


class Challenge(BaseIcpcChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """

    def play(self, *extra):
        if extra:
            if len(extra) != 2:
                raise Exception(f"Expected 2 arguments, got {len(extra)}: {extra}")
            input_number, case_index = map(int, extra)
        else:
            input_number, case_index = 1, 0
        print(f"{input_number},{case_index}")
        while True:
            self.output_mountain_from_file(input_number, case_index)
            user_input = click.prompt("Enter an input number and a case index")
            if user_input.lower() == "r":
                print(f"Restarting...")
                return restart_process()
            input_number, case_index = [int(part.strip()) for part in user_input.strip().split(",")]

    def output_mountain_from_file(self, input_number: int, case_index: int) -> None:
        if input_number < 0:
            prefix = f"sample-{-input_number}"
        else:
            prefix = f"secret-{input_number:02}"
        input_file, = (Path(__file__).parent / "data" / "G-lavamoat").glob(f"{prefix}*.in")
        cases = Mountain.split_cases(input_file.read_text())
        print(f"{len(cases)} cases in {input_file.name}")
        if case_index >= len(cases):
            print(f"Choose a case index between 0 and {len(cases) - 1}")
            return
        mountain = Mountain.from_text(cases[case_index])
        viable_side_ranges = MountainSolver.from_mountain(mountain)\
            .get_all_viable_side_ranges()
        if viable_side_ranges:
            ranges_str = "\n".join(
                f' * {y_start}-{y_end}'
                if not almost_equals(y_start, y_end) else
                f' * {y_start}'
                for side_range in viable_side_ranges
                for y_start, y_end in [side_range.get_y_range()]
            )
            print(f"Got {e_success('viable Ys')}:\n{ranges_str}")
        else:
            print(f"{e_error('No Y viable')} ranges")
        output_file = Path(__file__).parent / "problem_g_output.svg"
        output_file.write_text(self.to_svg_text(mountain))
        print(f"Open file://{output_file.absolute()}\nPress any key")

    def to_svg_text(self, mountain, max_width: int = 2000, max_height: int = 1000) -> str:
        svg_width = max_width
        svg_height = max_height
        # if mountain.width / max_width >= mountain.height / max_height:
        #     svg_width = max_width
        #     svg_height = svg_width * mountain.height // mountain.width
        # else:
        #     svg_height = max_height
        #     svg_width = svg_height * mountain.width // mountain.height
        svg_width_factor = svg_width / mountain.width
        svg_height_factor = svg_height / mountain.height

        hills_and_possible_hills = [
            (hill, hill.get_possible_hills())
            for hill in mountain.hills
        ]

        return """
            <svg viewBox='0 0 {width} {height}' width='{width}' height='{height}' style='background-color: white;' xmlns='http://www.w3.org/2000/svg'>
                <defs>
                    <filter x="0" y="0" width="1" height="1" id="solid">
                        <feFlood flood-color="yellow" result="bg" />
                        <feMerge>
                            <feMergeNode in="bg"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                    <pattern id="pattern-stripe" 
                        width="10" height="10" 
                        patternUnits="userSpaceOnUse"
                        patternTransform="rotate(45)">
                        <rect width="5" height="10" transform="translate(0,0)" fill="white"></rect>
                    </pattern>
                    <mask id="mask-stripe">
                        <rect x="0" y="0" width="100%" height="100%" fill="url(#pattern-stripe)" />
                    </mask>     
                    <style type="text/css"><![CDATA[
                        {style}
                    ]]></style>
                </defs>
                {triangles}
                <g class='ribbons' />
                <polyline class='mouse-polyline' />
                <text class='path-length' x='10' y='25' />
                <script type='text/javascript'><![CDATA[
                    {data}
                    {script}
                ]]></script>
            </svg>
        """.format(
            width=svg_width,
            height=svg_height,
            style=(Path(__file__).parent  / "problem_g_style.css").read_text(),
            triangles="<g class='triangles'>{}</g>".format("\n".join([
                polygon
                for hill, (min_possible_hill, max_possible_hill) in hills_and_possible_hills
                for polygon in [
                    "<polygon class='triangle' points='{points}' />".format(
                        points=" ".join(
                            f"{point.x * svg_width_factor},{point.y * svg_height_factor}"
                            for point in hill.points
                        ),
                        zs=" ".join(f"{point.z}" for point in hill.points)
                    ),
                    "<polygon class='triangle min' points='{points}' />".format(
                        points=" ".join(
                            f"{point.x * svg_width_factor},{point.y * svg_height_factor}"
                            for point in min_possible_hill.points
                        ),
                        zs=" ".join(f"{point.z}" for point in min_possible_hill.points)
                    ),
                    "<polygon class='triangle max' points='{points}' />".format(
                        points=" ".join(
                            f"{point.x * svg_width_factor},{point.y * svg_height_factor}"
                            for point in max_possible_hill.points
                        ),
                        zs=" ".join(f"{point.z}" for point in max_possible_hill.points)
                    ),
                ]
            ])),
            data="const data = {data};".format(
                data=json.dumps([
                    {
                        "points": [
                            {
                                "x": point.x * svg_width_factor,
                                "y": point.y * svg_height_factor,
                                "z": point.z
                            }
                            for point in hill.points
                        ],
                        "min": [
                            {
                                "x": point.x * svg_width_factor,
                                "y": point.y * svg_height_factor,
                                "z": point.z
                            }
                            for point in min_possible_hill.points
                        ],
                        "max": [
                            {
                                "x": point.x * svg_width_factor,
                                "y": point.y * svg_height_factor,
                                "z": point.z
                            }
                            for point in max_possible_hill.points
                        ],
                        "direction": {
                            "x": direction.x * svg_width_factor,
                            "y": direction.y * svg_height_factor,
                        },
                        "named": {
                            "min": {
                                "x": min_point.x * svg_width_factor,
                                "y": min_point.y * svg_height_factor,
                                "z": min_point.z
                            },
                            "mid": {
                                "x": mid_point.x * svg_width_factor,
                                "y": mid_point.y * svg_height_factor,
                                "z": mid_point.z
                            },
                            "max": {
                                "x": max_point.x * svg_width_factor,
                                "y": max_point.y * svg_height_factor,
                                "z": max_point.z
                            },
                            "new": {
                                "x": new_point.x * svg_width_factor,
                                "y": new_point.y * svg_height_factor,
                                "z": new_point.z
                            },
                            "new_factor": new_factor,
                        },
                    }
                    for hill, (min_possible_hill, max_possible_hill) in hills_and_possible_hills
                    for direction in [hill.get_direction()]
                    for [min_point, mid_point, max_point, new_point, new_factor] in [hill.four_points_and_factor]
                ], indent=2),
            ),
            script=(Path(__file__).parent  / "problem_g_script.js").read_text(),
        )


@dataclass
class MountainSolver:
    mountain: "Mountain"
    hill_side_map: "HillSideMap"

    @classmethod
    def from_mountain(cls, mountain: "Mountain") -> "MountainSolver":
        return cls(mountain=mountain, hill_side_map=HillSideMap.from_mountain(mountain))

    def get_all_viable_side_ranges(self):
        first_side_ranges = self.get_first_side_ranges()
        side_ranges = self.get_all_side_ranges(first_side_ranges)
        end_ranges = self.get_all_end_side_ranges(side_ranges)
        reverse_side_ranges = self.get_all_side_ranges(end_ranges)
        reverse_end_side_ranges = self.get_all_end_side_ranges(reverse_side_ranges, match_x=0)
        merged_side_ranges = self.merge_side_ranges(reverse_end_side_ranges)
        print(f"{len(first_side_ranges)} first side ranges")
        print(f"{len(side_ranges)} side ranges")
        print(f" * {', '.join(map(str, (self.mountain.hills.index(side_range.hill) for side_range in side_ranges)))}")
        print(f"{len(end_ranges)} end side ranges")
        print(f"{len(reverse_side_ranges)} reverse side ranges")
        print(f"{len(reverse_end_side_ranges)} reverse end side ranges")
        print(f"{len(merged_side_ranges)} merged side ranges")
        return merged_side_ranges

    def merge_side_ranges(self, side_ranges: List["SideRange"]) -> List["SideRange"]:
        side_ranges_by_hill_and_side: Dict["Hill", Dict[SideKey, List[SideRange]]] = {}
        for side_range in side_ranges:
            side_ranges_by_hill_and_side\
                .setdefault(side_range.hill, {})\
                .setdefault(side_range.side.key, list())\
                .append(side_range)
        merged_side_ranges: List[SideRange] = []
        for side_map in side_ranges_by_hill_and_side.values():
            for group in side_map.values():
                sorted_group = sorted(group, key=lambda _side_range: _side_range.start)
                previous = None
                for side_range in sorted_group:
                    if previous is None:
                        previous = side_range
                        continue
                    if side_range.start > previous.end and not almost_equals(side_range.start, previous.end):
                        merged_side_ranges.append(previous)
                        previous = side_range
                        continue
                    previous = previous.replace(end=side_range.end)
                if previous:
                    merged_side_ranges.append(previous)
        merged_side_ranges.sort(key=lambda _side_range: _side_range.min_y)
        return merged_side_ranges

    def get_all_end_side_ranges(self, all_side_ranges: Optional[List["SideRange"]] = None, match_x: int = None) -> List["SideRange"]:
        if all_side_ranges is None:
            all_side_ranges = self.get_all_side_ranges()
        if match_x is None:
            match_x = self.mountain.width
        return [
            contracted_side_range
            for side_range in all_side_ranges
            for contracted_side_range in [side_range.contract_if_matches(match_x)]
            if contracted_side_range
        ]

    def get_all_side_ranges(self, first_side_ranges: Optional[List["SideRange"]] = None) -> List["SideRange"]:
        if first_side_ranges is None:
            first_side_ranges = self.get_first_side_ranges()
        side_ranges = list(first_side_ranges)
        previous_side_ranges_and_seen = [
            (side_range, {side_range.hill})
            for side_range in side_ranges
        ]
        while previous_side_ranges_and_seen:
            next_side_ranges_and_seen, next_terminal_side_ranges = self.get_next_side_ranges_and_seen(previous_side_ranges_and_seen)
            side_ranges.extend(next_side_range for next_side_range, _ in next_side_ranges_and_seen)
            side_ranges.extend(next_terminal_side_ranges)
            previous_side_ranges_and_seen = next_side_ranges_and_seen
        return side_ranges

    def get_next_side_ranges_and_seen(self, side_ranges_and_seen: "SideRangesAndSeen") -> Tuple["SideRangesAndSeen", List["SideRange"]]:
        """
        >>> solver = Mountain.from_text(VIABLE_EXAMPLE_INPUT).get_solver()
        >>> first_side_ranges = solver.get_first_side_ranges()
        >>> second_side_ranges_and_seen, second_terminals = solver.get_next_side_ranges_and_seen([
        ...     (_side_range, {_side_range.hill}) for _side_range in first_side_ranges])
        >>> show_side_ranges(_side_range for _side_range, _ in second_side_ranges_and_seen)
        [((0, 6), (4, 3), 0.0, ...)]
        >>> show_side_ranges(second_terminals)
        []
        >>> third_side_ranges_and_seen, third_terminals = solver.get_next_side_ranges_and_seen([
        ...     (_side_range, {_side_range.hill}) for _side_range in second_side_ranges])
        >>> show_side_ranges(_side_range for _side_range, _ in third_side_ranges_and_seen)
        [((0, 6), (4, 3), 0.0, ...)]
        >>> show_side_ranges(third_terminals)
        []
        """
        next_side_ranges_and_seen = [
            (next_side_range, seen)
            for side_range, seen in side_ranges_and_seen
            for next_side_range in self.get_next_side_ranges(side_range)
        ]
        translated_next_side_ranges_and_seen = [
            (translated_next_side_range, seen | {translated_next_side_range.hill})
            for next_side_range, seen in next_side_ranges_and_seen
            for translated_next_side_range
            in [self.translate_side_range_to_next_triangle(next_side_range)]
            if translated_next_side_range
            and not translated_next_side_range.hill in seen
        ]
        terminal_side_ranges = [
            next_side_range
            for next_side_range, seen in next_side_ranges_and_seen
            if not self.hill_side_map.get_from_side_range(next_side_range)
        ]
        return translated_next_side_ranges_and_seen, terminal_side_ranges

    def get_first_side_ranges(self) -> List["SideRange"]:
        """
        >>> show_side_ranges(
        ...     Mountain.from_text(VIABLE_EXAMPLE_INPUT).get_solver().get_first_side_ranges())
        [((0, 0), (0, 6), 0, 1)]
        """
        side_ranges = []
        for hill in self.mountain.hills:
            sides = [side for side in hill.sides if side.is_on_x(0)]
            if not sides:
                continue
            side, = sides
            side_ranges.append(SideRange.from_hill_and_side(hill, side))
        return side_ranges

    def translate_side_range_to_next_triangle(self, side_range: "SideRange") -> Optional["SideRange"]:
        """
        >>> solver = Mountain.from_text(VIABLE_EXAMPLE_INPUT).get_solver()
        >>> first_side_ranges = solver.get_first_side_ranges()
        >>> second_side_ranges = [
        ...     solver.translate_side_range_to_next_triangle(next_side_range)
        ...     for _side_range in first_side_ranges
        ...     for next_side_range in solver.get_next_side_ranges(_side_range)
        ... ]
        >>> show_side_ranges(second_side_ranges)
        [((0, 6), (4, 3), 0.0, ...)]
        >>> third_side_ranges = [
        ...     solver.translate_side_range_to_next_triangle(next_side_range)
        ...     if solver.hill_side_map.get_from_side_range(next_side_range) else
        ...     None
        ...     for _side_range in second_side_ranges
        ...     if _side_range
        ...     for next_side_range in solver.get_next_side_ranges(_side_range)
        ... ]
        >>> show_side_ranges(third_side_ranges)
        [None, ((2, 6), (4, 3), 0, ...)]
        """
        next_hill_and_side = self.hill_side_map.get_from_side_range(side_range)
        if not next_hill_and_side:
            return None
        next_hill, next_side = next_hill_and_side
        current_hill = side_range.hill
        current_side = side_range.side
        start = side_range.start
        end = side_range.end
        if current_hill.get_low_and_high_for_side(current_side) == next_hill.get_low_and_high_for_side(current_side):
            return SideRange(hill=next_hill, side=next_side, start=start, end=end)
        else:
            return SideRange(hill=next_hill, side=next_side, start=1 - end, end=1 - start)

    def get_next_side_ranges(self, side_range: "SideRange") -> List["SideRange"]:
        """
        >>> solver = Mountain.from_text(VIABLE_EXAMPLE_INPUT).get_solver()
        >>> first_side_ranges = solver.get_first_side_ranges()
        >>> second_side_ranges = [
        ...     next_side_range
        ...     for _side_range in first_side_ranges
        ...     for next_side_range in solver.get_next_side_ranges(_side_range)
        ... ]
        >>> show_side_ranges(second_side_ranges)
        [((0, 6), (4, 3), 0.0, ...)]
        >>> third_side_ranges = [
        ...     next_side_range
        ...     for _side_range in second_side_ranges
        ...     for translated_side_range in [solver.translate_side_range_to_next_triangle(_side_range)]
        ...     if translated_side_range
        ...     for next_side_range in solver.get_next_side_ranges(translated_side_range)
        ... ]
        >>> show_side_ranges(third_side_ranges)
        [((0, 6), (2, 6), 0.0, 1), ((2, 6), (4, 3), 0, ...)]
        """
        hill = side_range.hill
        side = side_range.side
        start = side_range.start
        end = side_range.end
        new_factor = hill.new_factor
        if side.has_min and side.has_mid:
            return [
                SideRange(
                    hill=hill,
                    side=hill.min_max_side,
                    start=start * new_factor,
                    end=end * new_factor,
                ),
            ]
        if side.has_mid and side.has_max:
            return [
                SideRange(
                    hill=hill,
                    side=hill.min_max_side,
                    start=new_factor + start * (1 - new_factor),
                    end=new_factor + end * (1 - new_factor),
                ),
            ]
        if not (side.has_min and side.has_max):
            raise Exception(f"Side {side} did not match points {[hill.min_point, hill.mid_point, hill.max_point]}")
        if end <= new_factor:
            return [
                SideRange(
                    hill=hill,
                    side=hill.min_mid_side,
                    start=start / new_factor,
                    end=end / new_factor,
                ),
            ]
        if new_factor <= start:
            return [
                SideRange(
                    hill=hill,
                    side=hill.mid_max_side,
                    start=(start - new_factor) / (1 - new_factor),
                    end=(end - new_factor) / (1 - new_factor),
                ),
            ]
        return [
            SideRange(
                hill=hill,
                side=hill.min_mid_side,
                start=start / new_factor,
                end=1,
            ),
            SideRange(
                hill=hill,
                side=hill.mid_max_side,
                start=0,
                end=(end - new_factor) / (1 - new_factor),
            ),
        ]


SideRangesAndSeen = List[Tuple["SideRange", Set["Hill"]]]


@dataclass(frozen=True)
class SideRange:
    hill: "Hill"
    side: "Side"
    start: float
    end: float

    @classmethod
    def from_hill_and_side(cls, hill: "Hill", side: "Side") -> "SideRange":
        return SideRange(hill=hill, side=side, start=0, end=1)

    def contract_if_matches(self, match_x: float) -> Optional["SideRange"]:
        first_equals = almost_equals(self.side.points[0].x, match_x)
        if first_equals and almost_equals(self.start, 0):
            return self.replace(end=0)
        second_equals = almost_equals(self.side.points[1].x, match_x)
        if second_equals and almost_equals(self.end, 1):
            return self.replace(start=1)
        if first_equals and second_equals:
            return self
        return None

    def replace(self, start: Optional[float] = None, end: Optional[float] = None) -> "SideRange":
        if start is None:
            start = self.start
        if end is None:
            end = self.end
        return SideRange(hill=self.hill, side=self.side, start=start, end=end)

    @cached_property
    def min_y(self) -> float:
        return self.side.min_y

    def get_y_range(self) -> Tuple[float, float]:
        first = self.side.points[0].y
        second = self.side.points[1].y
        y_range = (
            first + (second - first) * self.start,
            first + (second - first) * self.end,
        )
        if first > second:
            y_range = y_range[::-1]
        return y_range


DefaultDelta = 0.00001


def almost_equals(left: float, right: float, delta: float = DefaultDelta) -> bool:
    return abs(left - right) <= delta


@dataclass
class HillSideMap:
    side_map: Dict["Hill", Dict["SideKey", Tuple["Hill", "Side"]]]

    @classmethod
    def from_mountain(cls, mountain: "Mountain") -> "HillSideMap":
        hills_by_side = HillsBySide.from_mountain(mountain)
        side_map = {}
        for hill in mountain.hills:
            for side in hill.sides:
                other_hills = hills_by_side[side] - {hill}
                if not other_hills:
                    continue
                if len(other_hills) > 1:
                    nl = "\n"
                    raise Exception(
                        f"There were too many other hills for hill #{mountain.hills.index(hill)} and {side}:\n"
                        f"{', '.join(map(str, map(mountain.hills.index, other_hills)))}, with sides:\n"
                        f"{nl.join(', '.join(map(str, (other_side for other_side in other_hill.sides if other_side.key == side.key))) for other_hill in other_hills)}"
                    )
                other_hill, = other_hills
                side_map.setdefault(hill, {})[side.key] = other_hill, other_hill.get_side(side)
        return cls(side_map=side_map)

    def get(self, hill: "Hill", side: "Side") -> Optional[Tuple["Hill", "Side"]]:
        return self.side_map[hill].get(side.key)

    def get_from_side_range(self, side_range: "SideRange") -> Optional[Tuple["Hill", "Side"]]:
        return self.get(side_range.hill, side_range.side)


@dataclass
class HillsBySide:
    by_side_key: Dict["SideKey", Set["Hill"]]

    @classmethod
    def from_mountain(cls, mountain: "Mountain") -> "HillsBySide":
        by_side_key = {}
        for hill in mountain.hills:
            for side in hill.sides:
                by_side_key.setdefault(side.key, set()).add(hill)
        return cls(by_side_key=by_side_key)

    def __getitem__(self, item: "Side") -> Set["Hill"]:
        return self.by_side_key[item.key]


@dataclass
class Mountain:
    hills: List["Hill"]
    width: int
    height: int

    @classmethod
    def split_cases(cls, text: str) -> List[str]:
        lines = (
            line.strip()
            for line in text.strip().splitlines()
        )
        next(lines)
        cases = []
        while True:
            try:
                first_line = next(lines)
            except StopIteration:
                break
            _, _, point_count, side_count = map(int, first_line.strip().split(" "))
            case_lines = [first_line] + [
                next(lines)
                for _ in range(point_count + side_count)
            ]
            cases.append("\n".join(case_lines))
        return cases

    @classmethod
    def from_text(cls, text: str) -> "Mountain":
        """
        >>> len(Mountain.from_text('''
        ...     6 6 4 2
        ...     0 0 1
        ...     6 0 2
        ...     6 6 4
        ...     0 6 3
        ...     1 2 3
        ...     1 3 4
        ... ''').hills)
        2
        """
        lines = (
            map(int, line.strip().split(" "))
            for line in text.strip().splitlines()
        )
        width, height, point_count, side_count = next(lines)
        points = [
            Point3D(*next(lines))
            for _ in range(point_count)
        ]
        # noinspection PyTypeChecker
        hills = [
            Hill.from_points_and_indexes(points, next(lines))
            for _ in range(side_count)
        ]
        return cls(hills=hills, width=width, height=height)

    def get_solver(self) -> "MountainSolver":
        return MountainSolver.from_mountain(self)


@dataclass(frozen=True)
class Hill:
    points: Tuple[Point3D, Point3D, Point3D]

    @classmethod
    def from_points_and_indexes(cls, points: List[Point3D], indexes: Tuple[int, int, int]) -> "Hill":
        # noinspection PyTypeChecker
        return cls(points=tuple(points[index - 1] for index in indexes))

    def replacing(self, old_point: Point3D, new_point: Point3D) -> "Hill":
        new_points = list(self.points)
        new_points[new_points.index(old_point)] = new_point
        # noinspection PyTypeChecker
        return Hill(points=tuple(new_points))

    def get_possible_hills(self) -> Tuple["Hill", "Hill"]:
        min_point, _, max_point, new_point, _ = self.four_points_and_factor
        return self.replacing(max_point, new_point), self.replacing(min_point, new_point)

    def get_direction(self) -> Point2D:
        _, mid_point, _, new_point, _ = self.four_points_and_factor
        return Point2D(new_point.x - mid_point.x, new_point.y - mid_point.y)

    @cached_property
    def four_points_and_factor(self) -> Tuple[Point3D, Point3D, Point3D, Point3D, float]:
        max_point, mid_point, min_point = sorted(self.points, key=lambda point: point.z, reverse=True)
        new_factor = (mid_point.z - min_point.z) / (max_point.z - min_point.z)
        new_point = min_point.offset(max_point.difference(min_point).resize(new_factor))
        return min_point, mid_point, max_point, new_point, new_factor

    @cached_property
    def min_point(self) -> Point3D:
        min_point, _, _, _, _ = self.four_points_and_factor
        return min_point

    @cached_property
    def mid_point(self) -> Point3D:
        _, mid_point, _, _, _ = self.four_points_and_factor
        return mid_point

    @cached_property
    def max_point(self) -> Point3D:
        _, _, max_point, _, _ = self.four_points_and_factor
        return max_point

    @cached_property
    def new_factor(self) -> float:
        min_point, mid_point, max_point, new_point, new_factor = self.four_points_and_factor
        return new_factor

    @cached_property
    def min_mid_side(self) -> "Side":
        return Side(points=(self.min_point, self.mid_point), has_min=True, has_mid=True, has_max=False)

    @cached_property
    def mid_max_side(self) -> "Side":
        return Side(points=(self.mid_point, self.max_point), has_min=False, has_mid=True, has_max=True)

    @cached_property
    def min_max_side(self) -> "Side":
        return Side(points=(self.min_point, self.max_point), has_min=True, has_mid=False, has_max=True)

    @cached_property
    def sides(self) -> List["Side"]:
        return [
            self.min_mid_side,
            self.mid_max_side,
            self.min_max_side,
        ]

    def has_x(self, x: float) -> bool:
        return sum(1 for point in self.points if point.x == x) == 2

    @cached_property
    def sides_by_key(self) -> Dict["SideKey", "Side"]:
        return {
            side.key: side
            for side in self.sides
        }

    def get_side(self, side: "Side") -> "Side":
        return self.sides_by_key[side.key]

    def get_low_and_high_for_side(self, side: "Side") -> Tuple[Point3D, Point3D]:
        if side.has_min:
            next_low = self.min_point
            if side.has_mid:
                next_high = self.mid_point
            else:
                next_high = self.max_point
        else:
            next_low = self.mid_point
            next_high = self.max_point
        return next_low, next_high


SideKey = Tuple[Point3D, Point3D]


@dataclass(frozen=True)
class Side:
    points: Tuple[Point3D, Point3D]
    has_min: bool
    has_mid: bool
    has_max: bool

    @cached_property
    def key(self) -> SideKey:
        if self.points[0][:2] <= self.points[1][:2]:
            return self.points
        # noinspection PyTypeChecker
        return self.points[::-1]

    def is_on_x(self, x: float) -> bool:
        """
        >>> Side(points=(Point3D(x=0, y=0, z=374), Point3D(x=0, y=111, z=638)),
        ...     has_min=True, has_mid=True, has_max=False).is_on_x(0)
        True
        >>> Side(points=(Point3D(x=0, y=0, z=374), Point3D(x=1, y=58, z=653)),
        ...     has_min=True, has_mid=True, has_max=False).is_on_x(0)
        False
        >>> Side(points=(Point3D(x=0, y=0, z=374), Point3D(x=15, y=24, z=771)),
        ...     has_min=False, has_mid=True, has_max=True).is_on_x(0)
        False
        >>> Side(points=(Point3D(x=36, y=2, z=338), Point3D(x=15, y=24, z=771)),
        ...     has_min=True, has_mid=False, has_max=True).is_on_x(0)
        False
        """
        return (
            almost_equals(self.points[0].x, x)
            and almost_equals(self.points[1].x, x)
        )

    @cached_property
    def min_y(self) -> float:
        return min(self.points[0].y, self.points[1].y)


VIABLE_EXAMPLE_INPUT = """
10 6 7 7
6 1 8
10 0 10
10 6 4
2 6 6
0 6 0
4 3 11
0 0 7
2 1 7
2 3 1
3 6 1
3 4 6
6 4 5
5 7 6
7 1 6
"""


def show_side_ranges(side_ranges: List[Optional["SideRange"]]) -> List[Optional[Tuple]]:
    return list(map(show_side_range, side_ranges))


def show_side_range(side_range: Optional["SideRange"]) -> Optional[Tuple]:
    if not side_range:
        return None
    return (
        side_range.side.key[0][:2],
        side_range.side.key[1][:2],
        side_range.start, side_range.end,
    )


Challenge.main()
challenge = Challenge()
