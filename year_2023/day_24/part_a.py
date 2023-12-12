#!/usr/bin/env python3
from dataclasses import dataclass
import re
from pathlib import Path
from typing import ClassVar, Dict, Iterable, List, Optional, Set, Tuple, Union

import click

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Point3D, reframe


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        20361
        """
        min_value = 200000000000000
        max_value = 400000000000000
        boundaries = (
            Point3D(min_value, min_value, min_value),
            Point3D(max_value, max_value, max_value),
        )
        return Cloud.from_text(_input).get_intersection_count_in_future_and_space(boundaries, in_3d=False)

    def play(self):
        cloud = Cloud.from_text(self.input)
        min_value = 200000000000000
        max_value = 400000000000000
        boundaries = (
            Point2D(min_value, min_value),
            Point2D(max_value, max_value),
        )
        while True:
            user_input = click.prompt(f"Enter indexes X,X [0-{len(cloud.hailstones) - 1}]")
            try:
                left_index, right_index = map(int, user_input.split(","))
            except ValueError:
                print(f"Could not parse '{user_input}'")
                continue
            left = cloud.hailstones[left_index]
            colliding_hailstones = [
                right
                for right in cloud.hailstones
                if right != left
                for (time, everywhere) in [left.get_intersection_time(right)]
                if time is not None or everywhere
            ]
            print(f"#{left_index} {left} colliding with {len(colliding_hailstones)} hailstones")
            for right in colliding_hailstones:
                print(f" * {cloud.hailstones.index(right)}#: {left.get_intersection_position(right, round_digits=3)} @ {left.get_intersection_time(right)}/{right.get_intersection_time(left)}")
            right = cloud.hailstones[right_index]
            print(f"With #{right_index} {right}")
            self.print_graph(left, right, 0, 1, boundaries)
            print(f"Intersection at {left.get_intersection_position_at_plane(right, 0, 1, round_digits=3)}")
            self.print_graph(left, right, 0, 2, boundaries)
            print(f"Intersection at {left.get_intersection_position_at_plane(right, 0, 2, round_digits=3)}")
            self.print_graph(left, right, 1, 2, boundaries)
            print(f"Intersection at {left.get_intersection_position_at_plane(right, 1, 2, round_digits=3)}")
            self.output_html(cloud, left_index, right_index, boundaries)

    def output_html(self, cloud: "Cloud", preferred_left_index: int, preferred_right_index: int, boundaries: Tuple[Point2D, Point2D], draw_size: Tuple[int, int] = (1000, 1000)):
        left_line_styles = "\n".join(
            f"""
            label:has(.left-select > option[value='{left_index}']:checked) ~ svg .line-left-{left_index} {{
                display: initial;
            }}
            """
            for left_index in [preferred_left_index]
            # for left_index in range(len(cloud.hailstones))
        )
        right_line_styles = "\n".join(
            f"""
            label:has(.right-select > option[value='{right_index}']:checked) ~ svg .line-right-{right_index} {{
                display: initial;
            }}
            """
            for right_index in range(len(cloud.hailstones))
        )
        point_styles = "\n".join(
            f"""
            label:has(.left-select > option[value='{left_index}']:checked) ~ label:has(.right-select > option[value='{right_index}']:checked) ~ svg .point-{left_index}-{right_index} {{
                display: initial;
            }}
            """
            for left_index in range(len(cloud.hailstones))
            for right_index in range(len(cloud.hailstones))
        )
        left_select_options = "\n".join(
            f"""
            <option value={left_index} {'selected' if left_index == preferred_left_index else ''}>{left_index}</option>
            """
            for left_index in [preferred_left_index]
            # for left_index in range(len(cloud.hailstones))
        )
        right_select_options = "\n".join(
            f"""
            <option value={right_index} {'selected' if right_index == preferred_right_index else ''}>{right_index}</option>
            """
            for right_index in range(len(cloud.hailstones))
        )
        left_lines = "\n".join(
            self.get_left_plane_html(cloud.hailstones[left_index], left_index, first_index, second_index, boundaries, draw_size)
            for left_index in [preferred_left_index]
            # for left_index in range(len(cloud.hailstones))
            for first_index, second_index in [(0, 1), (0, 2), (1, 2)]
        )
        right_lines = "\n".join(
            self.get_right_plane_html(cloud.hailstones[right_index], right_index, first_index, second_index, boundaries, draw_size)
            for right_index in range(len(cloud.hailstones))
            for first_index, second_index in [(0, 1), (0, 2), (1, 2)]
        )
        intersection_points = "\n".join(
            self.get_intersection_point_html(cloud.hailstones[left_index], cloud.hailstones[right_index], left_index, right_index, first_index, second_index, boundaries, draw_size)
            for left_index in [preferred_left_index]
            # for left_index in range(len(cloud.hailstones))
            for right_index in range(len(cloud.hailstones))
            for first_index, second_index in [(0, 1), (0, 2), (1, 2)]
        )
        _file = (Path(__file__).parent / "visualise.html")
        _file.write_text(f"""
            <html>
                <head>
                    <title>Visualise 2023/24/A</title>
                    <style type="text/css">
                        .line {{
                            display: none;
                        }}
                        {left_line_styles}
                        {right_line_styles}
                        .point {{
                            display: none;
                        }}
                        {point_styles}
                    </style>
                </head>
                <body>
                    <label>
                        Left:
                        <select class="left-select">
                            <option>None</option>
                            {left_select_options}
                        </select>
                    </label>
                    <label>
                        Right:
                        <select class="right-select">
                            <option>None</option>
                            {right_select_options}
                        </select>
                    </label>
                    <br>
                    <svg width={draw_size[0]} height={draw_size[1]} viewbox="0 0 {draw_size[0]} {draw_size[1]}">
                        {left_lines}
                        {right_lines}
                        {intersection_points}
                    </svg>
                </body>
            </html>
        """)
        print(f"Wrote to {_file.absolute()}")

    def get_left_plane_html(self, left: "Hailstone", left_index: int, first_index: int, second_index: int, boundaries: Tuple[Point2D, Point2D], draw_size: Tuple[int, int] = (1000, 1000)) -> str:
        left_points = self.get_graph_points(left, first_index, second_index, (boundaries[0].x, boundaries[1].x))
        graph_colour = {(0, 1): "red", (0, 2): "green", (1, 2): "blue"}[first_index, second_index]
        if len(left_points) != 2:
            return ""
        draw_boundaries = Point2D(0, 0), Point2D(draw_size[0], draw_size[1])
        draw_left_points = [point.reframe(*boundaries, *draw_boundaries).round() for point in left_points]
        return f"""
            <line
                class="line line-left-{left_index}"
                x1={draw_left_points[0].x}
                y1={draw_left_points[0].y}
                x2={draw_left_points[1].x}
                y2={draw_left_points[1].y}
                stroke={graph_colour}
            />
        """

    def get_right_plane_html(self, right: "Hailstone", right_index: int, first_index: int, second_index: int, boundaries: Tuple[Point2D, Point2D], draw_size: Tuple[int, int] = (1000, 1000)) -> str:
        right_points = self.get_graph_points(right, first_index, second_index, (boundaries[0].x, boundaries[1].x))
        graph_colour = {(0, 1): "red", (0, 2): "green", (1, 2): "blue"}[first_index, second_index]
        if len(right_points) != 2:
            return ""
        draw_boundaries = Point2D(0, 0), Point2D(draw_size[0], draw_size[1])
        draw_right_points = [point.reframe(*boundaries, *draw_boundaries).round() for point in right_points]
        return f"""
            <line
                class="line line-right-{right_index}"
                x1={draw_right_points[0].x}
                y1={draw_right_points[0].y}
                x2={draw_right_points[1].x}
                y2={draw_right_points[1].y}
                stroke={graph_colour}
            />
        """

    def get_intersection_point_html(self, left: "Hailstone", right: "Hailstone", left_index: int, right_index: int, first_index: int, second_index: int, boundaries: Tuple[Point2D, Point2D], draw_size: Tuple[int, int] = (1000, 1000)) -> str:
        point, everywhere = left.get_intersection_position_at_plane(right, first_index, second_index)
        if not point:
            return ""
        point = Point2D(point[first_index], point[second_index])
        draw_boundaries = Point2D(0, 0), Point2D(draw_size[0], draw_size[1])
        draw_right_point = point.reframe(*boundaries, *draw_boundaries).round()
        graph_colour = {(0, 1): "red", (0, 2): "green", (1, 2): "blue"}[first_index, second_index]
        return f"""
            <circle
                class="point point-{left_index}-{right_index}"
                cx={draw_right_point.x}
                cy={draw_right_point.y}
                r=5
                fill={graph_colour}
                data-point={point}
            />
        """

    def print_graph(self, left: "Hailstone", right: "Hailstone", first_index: int, second_index: int, boundaries: Tuple[Point2D, Point2D], draw_size: Tuple[int, int] = (10, 10)):
        left_points = self.get_graph_points(left, first_index, second_index, (boundaries[0].x, boundaries[1].x))
        right_points = self.get_graph_points(right, first_index, second_index, (boundaries[0].y, boundaries[1].y))
        graph_name = "".join(map({0: "X", 1: "Y", 2: "Z"}.get, [first_index, second_index]))
        if len(left_points) != 2 or len(right_points) != 2:
            print(f"Got {len(left_points)} left points and {len(right_points)} right points for {graph_name} of {left} and {right}")
            if len(left_points) == 4:
                print(f" * Left points: {left_points}")
            if len(right_points) == 4:
                print(f" * Right points: {right_points}")
            return
        # print(f"{graph_name} for left is {left_points[0]}-{left_points[1]}")
        # print(f"{graph_name} for right is {right_points[0]}-{right_points[1]}")
        draw_boundaries = Point2D(0, 0), Point2D(draw_size[0] - 1, draw_size[1] - 1)
        draw_left_points = [point.reframe(*boundaries, *draw_boundaries).round() for point in left_points]
        draw_right_points = [point.reframe(*boundaries, *draw_boundaries).round() for point in right_points]
        # print(f"Draw {graph_name} for left is {draw_left_points[0]}-{draw_left_points[1]}")
        # print(f"Draw {graph_name} for right is {draw_right_points[0]}-{draw_right_points[1]}")
        left_point_set = self.get_point_set(draw_left_points)
        right_point_set = self.get_point_set(draw_right_points)
        print(f"{graph_name} graph:")
        print("\n".join(
            "".join(
                "X"
                if point in left_point_set and point in right_point_set else
                "A"
                if point in left_point_set else
                "B"
                if point in right_point_set else
                " "
                for x in range(draw_size[0])
                for point in [Point2D(x, y)]
            )
            for y in range(draw_size[1])
        ))

    def get_point_set(self, points: List[Point2D]) -> Set[Point2D]:
        start, end = points
        x_count = abs(start.x - end.x) + 1
        y_count = abs(start.y - end.y) + 1
        invert = y_count > x_count
        if not invert:
            first_index = 0
            second_index = 1
        else:
            first_index = 1
            second_index = 0
        if start[first_index] <= end[first_index]:
            first_start = start[first_index]
            first_end = end[first_index]
            second_start = start[second_index]
            second_end = end[second_index]
        else:
            first_start = end[first_index]
            first_end = start[first_index]
            second_start = end[second_index]
            second_end = start[second_index]
        if first_start == first_end:
            return {Point2D(points[0])}
        first_range = range(first_start, first_end + 1)
        second_range = (round(reframe(first, first_start, first_end, second_start, second_end)) for first in first_range)
        if not invert:
            x_range, y_range = first_range, second_range
        else:
            x_range, y_range = second_range, first_range
        return {
            Point2D(x, y)
             for x, y in zip(x_range, y_range)
        }

    def get_graph_points(self, hailstone: "Hailstone", first_index: int, second_index: int, boundaries: Tuple[int, int]) -> List[Point2D]:
        min_value, max_value = boundaries
        bottom = self.get_graph_point(hailstone, first_index, second_index, True, min_value)
        top = self.get_graph_point(hailstone, first_index, second_index, True, max_value)
        left = self.get_graph_point(hailstone, first_index, second_index, False, min_value)
        right = self.get_graph_point(hailstone, first_index, second_index, False, max_value)
        return [
            point
            for point in [bottom, top, left, right]
            if min_value <= point.x <= max_value
            and min_value <= point.y <= max_value
        ]

    def get_graph_point(self, hailstone: "Hailstone", first_index: int, second_index: int, on_x: bool, value: int) -> Point2D:
        if on_x:
            return Point2D(
                value,
                (value - hailstone.position[first_index]) / hailstone.velocity[first_index] * hailstone.velocity[second_index] + hailstone.position[second_index]
            )
        else:
            return Point2D(
                (value - hailstone.position[second_index]) / hailstone.velocity[second_index] * hailstone.velocity[first_index] + hailstone.position[first_index],
                value,
            )


@dataclass
class Cloud:
    hailstones: List["Hailstone"]

    @classmethod
    def from_text(cls, text: str) -> "Cloud":
        """
        >>> len(Cloud.from_text('''
        ...     19, 13, 30 @ -2,  1, -2
        ...     18, 19, 22 @ -1, -1, -2
        ...     20, 25, 34 @ -2, -2, -4
        ...     12, 31, 28 @ -1, -2, -1
        ...     20, 19, 15 @  1, -5, -3
        ... ''').hailstones)
        5
        """
        return cls(hailstones=list(map(Hailstone.from_text, text.strip().splitlines())))

    def get_intersection_count_in_future_and_space(self, boundaries: Union[Tuple[Point2D, Point2D], Tuple[Point3D, Point3D]], in_3d: bool = True) -> int:
        """
        >>> Cloud.from_text('''
        ...     19, 13, 30 @ -2,  1, -2
        ...     18, 19, 22 @ -1, -1, -2
        ...     20, 25, 34 @ -2, -2, -4
        ...     12, 31, 28 @ -1, -2, -1
        ...     20, 19, 15 @  1, -5, -3
        ... ''').get_intersection_count_in_future_and_space((Point3D(7, 7, 7), Point3D(27, 27, 27)), in_3d=False)
        2
        """
        return sum(
            1
            for left_index, left in enumerate(self.hailstones)
            for right in self.hailstones[left_index + 1:]
            if left.intersects_in_future_and_space(right, boundaries, in_3d=in_3d)
        )

    def get_intersections_in_future_and_space(self, boundaries: Union[Tuple[Point2D, Point2D], Tuple[Point3D, Point3D]], in_3d: bool = True) -> Iterable[Tuple["Hailstone", "Hailstone", Point3D, float]]:
        return (
            (left, right, result, intersection_time)
            for left_index, left in enumerate(self.hailstones)
            for right in self.hailstones[left_index + 1:]
            for result, everywhere in [(left.get_intersection_position(right, in_3d=in_3d))]
            if result is not None
            for intersection_time, _ in [left.get_intersection_time(right, in_3d=in_3d)]
            if left.intersects_in_future_and_space(right, boundaries, in_3d=in_3d)
        )


@dataclass(frozen=True)
class Hailstone:
    position: Point3D
    velocity: Point3D

    re_text: ClassVar[re.Pattern] = re.compile(r"^(-?\d+),\s*(-?\d+),\s*(-?\d+)\s*@\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)$")

    @classmethod
    def from_text(cls, text: str) -> "Hailstone":
        """
        >>> print(Hailstone.from_text("19, 13, 30 @ -2,  1, -2"))
        19, 13, 30 @ -2, 1, -2
        """
        values_str = cls.re_text.match(text.strip()).groups()
        values = tuple(map(int, values_str))
        position = Point3D(*values[:3])
        velocity = Point3D(*values[3:])

        return cls(position=position, velocity=velocity)

    def __str__(self) -> str:
        return f"{', '.join(map(str, self.position))} @ {', '.join(map(str, self.velocity))}"

    def intersects_in_future_and_space(self, other: "Hailstone", boundaries: Union[Tuple[Point2D, Point2D], Tuple[Point3D, Point3D]], intersection: Optional[Tuple[Union[Point2D, Point3D], bool]] = None, in_3d: bool = True) -> bool:
        """
        >>> _boundaries = Point3D(7, 7, 7), Point3D(27, 27, 27)
        >>> def check_2d(left_text: str, right_text: str) -> bool:
        ...     return Hailstone.from_text(left_text).intersects_in_future_and_space(Hailstone.from_text(right_text), _boundaries, in_3d=False)
        >>> def check_3d(left_text: str, right_text: str) -> bool:
        ...     return Hailstone.from_text(left_text).intersects_in_future_and_space(Hailstone.from_text(right_text), _boundaries, in_3d=True)
        >>> check_2d("19, 13, 30 @ -2, 1, -2", "18, 19, 22 @ -1, -1, -2")
        True
        >>> check_3d("19, 13, 30 @ -2, 1, -2", "18, 19, 22 @ -1, -1, -2")
        False
        >>> check_2d("19, 13, 30 @ -2, 1, -2", "20, 25, 34 @ -2, -2, -4")
        True
        >>> check_3d("19, 13, 30 @ -2, 1, -2", "20, 25, 34 @ -2, -2, -4")
        False
        >>> check_2d("12, 31, 28 @ -1, -2, -1", "20, 19, 15 @ 1, -5, -3")
        False
        >>> check_3d("12, 31, 28 @ -1, -2, -1", "20, 19, 15 @ 1, -5, -3")
        False
        """
        if intersection is None:
            intersection = self.get_intersection_position(other, in_3d=in_3d)
        result, everywhere = intersection
        if everywhere:
            return True
        if result is None:
            return False
        in_boundaries = all(
            minimum <= value <= maximum
            for minimum, maximum, value in zip(*boundaries, result)
        )
        if not in_boundaries:
            return False
        time_self, _ = self.get_intersection_time(other, in_3d=in_3d, intersection=intersection)
        time_other, _ = other.get_intersection_time(self, in_3d=in_3d, intersection=intersection)
        if time_self is None or time_other is None:
            return False
        return time_self > 0 and time_other > 0

    def get_intersection_time(self, other: "Hailstone", in_3d: bool = True, intersection: Optional[Tuple[Union[Point2D, Point3D], bool]] = None) -> Tuple[Optional[float], bool]:
        if intersection is None:
            intersection = self.get_intersection_position(other, in_3d=in_3d)
        result, everywhere = intersection
        if everywhere:
            return None, True
        if result is None:
            return None, False
        for position, velocity, target in zip(self.position, self.velocity, result):
            if velocity == 0:
                continue
            return (target - position) / velocity, False
        raise Exception(f"Could not find intersection time between {self} and {other} with target {result}")

    def get_intersection_position(self, other: "Hailstone", in_3d: bool = True, round_digits: Optional[int] = -1) -> Tuple[Optional[Union[Point3D, Point2D]], bool]:
        """
        >>> def check_2d(left_text: str, right_text: str) -> Tuple[Union[Point3D], bool]:
        ...     return Hailstone.from_text(left_text).get_intersection_position(
        ...         Hailstone.from_text(right_text), in_3d=False, round_digits=3)
        >>> def check_3d(left_text: str, right_text: str) -> Union[Tuple[Union[Point3D], bool], Dict[Tuple[Hailstone, Hailstone], Tuple[Union[Point3D], bool]]]:
        ...     left = Hailstone.from_text(left_text)
        ...     right = Hailstone.from_text(right_text)
        ...     results: Dict[Tuple[Hailstone, Hailstone], Tuple[Union[Point2D, Point3D], bool]] = {}
        ...     for actual_left in {left, right}:
        ...         actual_right, = {left, right} - {actual_left}
        ...         for first_axis in {0, 1, 2}:
        ...             for second_axis in {0, 1, 2} - {first_axis}:
        ...                 third_axis, = {0, 1, 2} - {first_axis, second_axis}
        ...                 reordered_left = Hailstone(
        ...                     position=Point3D(actual_left.position[first_axis], actual_left.position[second_axis], actual_left.position[third_axis]),
        ...                     velocity=Point3D(actual_left.velocity[first_axis], actual_left.velocity[second_axis], actual_left.velocity[third_axis]),
        ...                 )
        ...                 reordered_right = Hailstone(
        ...                     position=Point3D(actual_right.position[first_axis], actual_right.position[second_axis], actual_right.position[third_axis]),
        ...                     velocity=Point3D(actual_right.velocity[first_axis], actual_right.velocity[second_axis], actual_right.velocity[third_axis]),
        ...                 )
        ...                 _result = reordered_left.get_intersection_position(reordered_right, in_3d=True, round_digits=3)
        ...                 if _result[0] is not None:
        ...                     reverse_first_axis = [first_axis, second_axis, third_axis].index(0)
        ...                     reverse_second_axis = [first_axis, second_axis, third_axis].index(1)
        ...                     reverse_third_axis = [first_axis, second_axis, third_axis].index(2)
        ...                     _result = Point3D(_result[0][reverse_first_axis], _result[0][reverse_second_axis], _result[0][reverse_third_axis]), _result[1]
        ...                 results[(reordered_left, reordered_right)] = _result
        ...     unique_results = set(results.values())
        ...     if len(unique_results) != 1:
        ...         return results
        ...     unique_result, = unique_results
        ...     return unique_result
        >>> check_3d("19, 13, 30 @ -2, 1, -2", "18, 19, 22 @ -1, -1, -2")
        (None, False)
        >>> check_3d("19, 13, 13 @ -2, 1, 1", "20, 25, 25 @ -2, -2, -2")
        (Point3D(x=11.667, y=16.667, z=16.667), False)
        >>> check_2d("19, 13, 30 @ -2, 1, -2", "18, 19, 22 @ -1, -1, -2")
        (Point2D(x=14.333, y=15.333), False)
        >>> check_3d("19, 13, 30 @ -2, 1, -2", "18, 19, 22 @ -1, -1, -2")
        (None, False)
        >>> check_2d("19, 13, 30 @ -2, 1, -2", "20, 25, 34 @ -2, -2, -4")
        (Point2D(x=11.667, y=16.667), False)
        >>> check_3d("19, 13, 30 @ -2, 1, -2", "20, 25, 34 @ -2, -2, -4")
        (None, False)
        >>> a = Hailstone.from_text("19, 13, 13 @ -2, 1, 1")
        >>> b = Hailstone.from_text("20, 25, 25 @ -2, -2, -2")
        >>> a.get_intersection_position(b, round_digits=3)
        (Point3D(x=11.667, y=16.667, z=16.667), False)
        >>> a = Hailstone.from_text("19, 13, 30 @ -2, 1, 0")
        >>> b = Hailstone.from_text("18, 19, 30 @ -1, -1, 0")
        >>> a.get_intersection_position(b, in_3d=False, round_digits=3)
        (Point2D(x=14.333, y=15.333), False)
        >>> a.get_intersection_position(b, round_digits=3)
        (Point3D(x=14.333, y=15.333, z=30.0), False)
        >>> a = Hailstone.from_text("19, 30, 13 @ -2, 0, 1")
        >>> b = Hailstone.from_text("18, 30, 19 @ -1, 0, -1")
        >>> a.get_intersection_position(b, in_3d=False, round_digits=3)
        (None, True)
        >>> a.get_intersection_position(b, round_digits=3)
        (Point3D(x=14.333, y=30.0, z=15.333), False)
        >>> a = Hailstone.from_text("19, 30, 13 @ 0, 0, 1")
        >>> b = Hailstone.from_text("19, 30, 19 @ 0, 0, -1")
        >>> a.get_intersection_position(b, in_3d=False, round_digits=3)
        (None, True)
        >>> a.get_intersection_position(b, round_digits=3)
        (None, True)
        """

        result_xy, xy_everywhere = self.get_intersection_position_at_plane(other, 0, 1, round_digits=round_digits)

        if not in_3d:
            if xy_everywhere:
                return None, True
            if result_xy is None:
                return None, False
            result_xy = result_xy.to_2d()
            return result_xy, False

        result_xz, xz_everywhere = self.get_intersection_position_at_plane(other, 0, 2, round_digits=round_digits)
        result_yz, yz_everywhere = self.get_intersection_position_at_plane(other, 1, 2, round_digits=round_digits)
        everywhere_count = sum(1 for result in [xy_everywhere, xz_everywhere, yz_everywhere] if result)
        non_null_results = {result_xy, result_xz, result_yz} - {None}
        if everywhere_count == 3:
            return None, True
        elif everywhere_count == 2:
            if not non_null_results:
                return None, False
            result, = non_null_results
            return result, False
        if len(non_null_results) == 1:
            result, = non_null_results
            return result, False
        return None, False

    def get_intersection_position_at_plane(self, other: "Hailstone", first_axis: int, second_axis: int, round_digits: Optional[int] = -1) -> Tuple[Optional[Point3D], bool]:
        pass
        """
        x1, y1, z1 @ vx1, vy1, z1
        x2, y2, z2 @ vx2, vy2, z2

        x1 + vx1 * t1 = x2 + vx2 * t2
        y1 + vy1 * t1 = y2 + vy2 * t2
        z1 + vz1 * t1 = z2 + vz2 * t2
        
        t1 = (x2 - x1 + vx2 * t2) / vx1
        t1 = (y2 - y1 + vy2 * t2) / vy1
        t1 = (z2 - z1 + vz2 * t2) / vz1
        
        (x2 - x1 + vx2 * t2) / vx1 = (y2 - y1 + vy2 * t2) / vy1
        (x2 - x1 + vx2 * t2) * vy1 = (y2 - y1 + vy2 * t2) * vx1
        t2 * (vy1 * vx2 - vx1 * vy2) = (y2 - y1) * vx1 - (x2 - x1) * vy1
        t2 = ((y2 - y1) * vx1 - (x2 - x1) * vy1) / (vy1 * vx2 - vx1 * vy2)
        """
        velocity_product = self.velocity[second_axis] * other.velocity[first_axis] - self.velocity[first_axis] * other.velocity[second_axis]
        if velocity_product == 0:
            if self.velocity[first_axis] == other.velocity[first_axis] == 0 and self.position[first_axis] == other.position[first_axis]:
                return None, True
            elif self.velocity[second_axis] == other.velocity[second_axis] == 0 and self.position[second_axis] == other.position[second_axis]:
                return None, True
            else:
                return None, False
        position_difference = self.position.offset(other.position, factor=-1)
        t2 = (-position_difference[second_axis] * self.velocity[first_axis] + position_difference[first_axis] * self.velocity[second_axis]) / velocity_product
        result = other.position.offset(other.velocity, factor=t2)
        if round_digits != -1:
            result = result.round(round_digits)
        return result, False


Challenge.main()
challenge = Challenge()
