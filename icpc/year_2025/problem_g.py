#!/usr/bin/env python3
import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
import re
from enum import Enum
from functools import cached_property
from itertools import groupby, zip_longest
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
        return "\n".join(map(str, (
            min_length
            if min_length is not None else
            "impossible"
            for case in Mountain.split_cases(_input)
            for min_length in [MountainSolver2.from_mountain(Mountain.from_text(case)).get_min_length()]
        )))

    def does_solution_match_output(self, result: str, output: str) -> bool:
        return all(
            almost_equal(result_value, output_value, delta=0.000001)
            if result_value is not None and output_value is not None else
            result_value == output_value
            for result_line, output_line in zip_longest(result.splitlines(), output.splitlines(), fillvalue="")
            for result_value in [None if result_line == "impossible" else float(result_line)]
            for output_value in [None if output_line == "impossible" else float(output_line)]
        )

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
                return restart_process(edit_args=lambda args: args[:args.index("play") + 1] + ["--", str(input_number), str(case_index)])
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
        y_ranges = MountainSolver2.from_mountain(mountain)\
            .get_viable_ys()
        if y_ranges:
            ranges_str = "\n".join(
                f' * {y_start}-{y_end}'
                if not almost_equal(y_start, y_end) else
                f' * {y_start}'
                for y_start, y_end in y_ranges
            )
            print(f"Got {e_success('viable Ys')}:\n{ranges_str}")
        else:
            print(f"{e_error('No Y viable')} ranges")
        length_range = MountainSolver2.from_mountain(mountain)\
            .get_total_length_range()
        if length_range:
            print(f"Got {e_success('viable lengths')}: {length_range[0]}-{length_range[1]}")
        else:
            print(f"{e_error('No viable lengths')}")
        output_file = Path(__file__).parent / "problem_g_output.html"
        output_file.write_text(self.to_html_text(mountain, input_name=input_file.name, input_number=input_number, case_index=case_index))
        print(f"Open file://{output_file.absolute()}\nPress any key")

    def to_html_text(self, mountain: "Mountain", input_name: str, input_number: int, case_index: int, max_width: int = 2000, max_height: int = 1000) -> str:
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
        solver = MountainSolver2.from_mountain(mountain)
        ribbons = solver.get_restricted_ribbons()
        if len(ribbons) > 100:
            print(f"Too many ribbons ({e_error(str(len(ribbons)))}), limiting to 100")
            ribbons = ribbons[:100]
        ribbon_histories = [
            {
                "history": [
                    {
                        "points": [
                            {
                                "x": point.x * svg_width_factor,
                                "y": point.y * svg_height_factor,
                            }
                            for point in ribbon_points
                        ],
                    }
                    for ribbon_points in ribbon.get_points_history()
                ],
                "final": solver.check_is_end_ribbon(ribbon),
            }
            for ribbon in ribbons
        ]

        return """
            <html>
                <head>
                    <title>{title}</title>
                    <link rel="stylesheet" type="text/css" href="problem_g_style.css">
                </head>
                <body>
                    <h2>{title}</h2>
                    <div>
                        <label><input type="checkbox" name="show-js-ribbons">Show JS ribbons</label>
                        <br>
                        <label><input type="checkbox" name="show-py-ribbons" checked>Show Python ribbons</label>
                        <label class='show-py-ribbons-radio'><input type='radio' name='show-py-ribbons-i' class='i-all' checked>All</label>
                        {py_ribbons_radios}
                        <br>
                        <label><input type="checkbox" name="show-min-max-triangles" checked>Show Min/Max triangles</label>
                    </div>
                    <style type="text/css">
                        {py_ribbons_style}
                    </style>
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
                        </defs>
                        {triangles}
                        <g class='ribbons' />
                        <g class='py-ribbons'>
                            {py_ribbons}
                        </g>
                        <polyline class='mouse-polyline' />
                        <text class='path-length' x='10' y='25' />
                        <text class='y-values' x='10' y='50' />
                    </svg>
                    <script type="text/javascript">
                        const svgWidth = {svg_width};
                        const svgHeight = {svg_height};
                        const svgWidthFactor = {svg_width_factor};
                        const svgHeightFactor = {svg_height_factor};
                        const data = {hill_data};
                        const ribbonHistories = {ribbon_data};
                    </script>
                    <script type="text/javascript" src="problem_g_script.js"></script>
                </body>
            </html>
        """.format(
            title=f"Mountain Visualization: {input_name} {input_number}-{case_index}",
            py_ribbons_radios="\n".join(
                f"<label class='show-py-ribbons-radio'><input type='radio' name='show-py-ribbons-i' class='i-{ribbon_index}'>#{ribbon_index + 1} ({len(ribbon_history['history'])})</label>"
                for ribbon_index, ribbon_history in enumerate(ribbon_histories)
            ),
            py_ribbons_style="\n".join(
                f'div:has(input[name="show-py-ribbons-i"].i-{ribbon_index}:not(:checked)):has(input[name="show-py-ribbons-i"].i-all:not(:checked)) ~ svg .ribbon.py.i-{ribbon_index} {{ display: none; }}'
                for ribbon_index in range(len(ribbon_histories))
            ),
            width=svg_width,
            height=svg_height,
            svg_width_factor=svg_width_factor,
            svg_height_factor=svg_height_factor,
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
            py_ribbons="\n".join([
                "<polygon class='ribbon py i-{index} {final_class}' points='{points}' />".format(
                    index=ribbon_index,
                    final_class='final' if ribbon_history["final"] else '',
                    points=' '.join(f'{point["x"]},{point["y"]}' for point in ribbon["points"]),
                )
                for ribbon_index, ribbon_history in enumerate(ribbon_histories)
                for ribbon in ribbon_history["history"]
            ]),
            svg_width=svg_width,
            svg_height=svg_height,
            hill_data=json.dumps([
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
            ribbon_data=json.dumps(ribbon_histories, indent=2),
        )


@dataclass
class MountainSolver2:
    mountain: "Mountain"
    hill_side_map: "HillSideMap"
    mid_point_hill_map: "MidPointHillMap"

    @classmethod
    def from_mountain(cls, mountain: "Mountain") -> "MountainSolver":
        return cls(
            mountain=mountain,
            hill_side_map=HillSideMap.from_mountain(mountain),
            mid_point_hill_map=MidPointHillMap.from_mountain(mountain),
        )

    def get_min_length(self) -> Optional[float]:
        length_range = self.get_total_length_range()
        if length_range is None:
            return None
        min_lenght, _ = length_range
        return min_lenght
    
    def get_total_length_range(self) -> Optional[Tuple[float, float]]:
        restricted_end_ribbons = self.get_restricted_end_ribbons()
        if not restricted_end_ribbons:
            return None
        min_length, max_length = restricted_end_ribbons[0].total_history_length_range()
        for ribbon in restricted_end_ribbons[1:]:
            ribbon_min_length, ribbon_max_length = ribbon.total_history_length_range()
            min_length = min(min_length, ribbon_min_length)
            max_length = max(max_length, ribbon_max_length)
        return min_length, max_length
    
    def get_viable_ys(self) -> List[Tuple[float, float]]:
        restricted_end_ribbons = self.get_restricted_end_ribbons()
        y_ranges = sorted(
            ribbon.end.get_y_range()
            for ribbon in restricted_end_ribbons
        )
        merged_y_ranges = []
        previous_y_range = None
        for y_range in y_ranges:
            if previous_y_range is None:
                previous_y_range = y_range
                continue
            if almost_greater(y_range[0], previous_y_range[1]):
                merged_y_ranges.append(previous_y_range)
                previous_y_range = y_range
                continue
            previous_y_range = previous_y_range[0], y_range[1]
        if previous_y_range:
            merged_y_ranges.append(previous_y_range)
        return merged_y_ranges
    
    def get_restricted_end_ribbons(self) -> List["Ribbon"]:
        end_ribbons = self.get_end_ribbons()
        return sorted((
            self.restrict_ribbon(ribbon)
            for ribbon in end_ribbons
        ), key=lambda ribbon: (ribbon.end.side.key, ribbon.end.start, ribbon.end.end))
    
    def get_restricted_ribbons(self) -> List["Ribbon"]:
        end_ribbons = self.get_ribbons()
        return sorted((
            self.restrict_ribbon(ribbon)
            for ribbon in end_ribbons
        ), key=lambda ribbon: (ribbon.end.side.key, ribbon.end.start, ribbon.end.end))
    
    def restrict_ribbon(self, ribbon) -> "Ribbon":
        history = list(ribbon.iterate_history())
        for index, node in enumerate(history[1:], start=1):
            if node.is_mid_point:
                continue
            next_node = history[index - 1]
            if next_node.is_mid_point:
                if not almost_equal(next_node.start.start, next_node.start.end):
                    raise Exception(f"Next ribbon is mid point, but it is not a single line:\n{next_node}")
                if almost_equal(next_node.start.start, 0):
                    next_mid_point = next_node.start.side.points[0]
                elif almost_equal(next_node.start.start, 1):
                    next_mid_point = next_node.start.side.points[1]
                else:
                    raise Exception(f"Next ribbon is mid point, but it does not start from the first or second point:\n{next_node}")
                if node.end.side.points[0] == next_mid_point:
                    if not almost_equal(node.end.start, 0):
                        raise Exception(f"Next ribbon is mid point, and this ribbon end should include it, but it starts from {node.end.start}")
                    end_side_range = node.end.replace(end=node.end.start)
                elif node.end.side.points[1] == next_mid_point:
                    if not almost_equal(node.end.end, 1):
                        raise Exception(f"Next ribbon is mid point, and this ribbon end should include it, but it ends at {node.end.end}")
                    end_side_range = node.end.replace(start=node.end.end)
                else:
                    raise Exception(f"Next ribbon is mid point, but this ribbon does not include the next mid point {next_mid_point}:\n{next_node}")
            else:
                end_side_range = self.translate_side_range(next_node.start)
                if end_side_range.hill != node.end.hill or end_side_range.side != node.end.side:
                    raise Exception(f"Cannot restrict ribbon history, got different end side range from {next_node}: {end_side_range} vs {node.start}")
                if almost_less(end_side_range.start, node.end.start) or almost_greater(end_side_range.end, node.end.end):
                    raise Exception(f"Cannot restrict ribbon history, got bigger end side range: start went from {node.start.start}-{node.start.end} to {start_side_range.start}-{start_side_range.end}")
            start_side_ranges = self.get_next_side_ranges(
                end_side_range, 
                # Prefer to keep the same side to make checks simpler
                prefer_min_mid_for_new_factor=node.start.side == node.start.hill.min_mid_side,
            )
            if len(start_side_ranges) != 1:
                raise Exception(f"Cannot restrict ribbon history, got multiple next side ranges from {end_side_range}: {start_side_ranges}")
            start_side_range, = start_side_ranges
            if start_side_range.hill != node.start.hill:
                raise Exception(f"Cannot restrict node history, got different start side range: hill went from {self.mountain.hills.index(node.start.hill)} to {self.mountain.hills.index(start_side_range.hill)}")
            if start_side_range.side != node.start.side:
                raise Exception(f"Cannot restrict node history, got different start side range: from {node.start.side} to {start_side_range.side}, and range from {node.start.start}-{node.start.end} to {start_side_range.start}-{start_side_range.end}. End side range went from {node.end.side} to {end_side_range.side}, and range from {node.end.start}-{node.end.end} to {end_side_range.start}-{end_side_range.end}")
            if almost_less(start_side_range.start, node.start.start) or almost_greater(start_side_range.end, node.start.end):
                raise Exception(f"Cannot restrict node history, got bigger start side range: start went from {node.start.start}-{node.start.end} to {start_side_range.start}-{start_side_range.end}, and end from {node.end.start}-{node.end.end} to {end_side_range.start}-{end_side_range.end}")
            history[index] = Ribbon(
                start=start_side_range,
                end=end_side_range, 
                is_mid_point=node.is_mid_point,
                previous=None,
            )

        for index, node in reversed(list(enumerate(history[:-1]))):
            previous_node = history[index + 1]
            history[index] = Ribbon(start=node.start, end=node.end, is_mid_point=node.is_mid_point, previous=previous_node)
        return history[0]

    def get_end_ribbons(self) -> List["Ribbon"]:
        """
        >>> solver = MountainSolver2.from_mountain(Mountain.from_text(VIABLE_EXAMPLE_INPUT_3))
        >>> show_ribbons(solver.get_end_ribbons())
        [(((5, 2), (6, 0), 0, 1.0), ((6, 0), (6, 10), 0.0, 0.2), 7),
            (((5, 2), (6, 10), 0.0, 0.12500000000000003),((6, 0), (6, 10), 0.2, 0.30000000000000004), 7),
            (((5, 2), (6, 10), 0.12500000000000003, 0.25),((6, 0), (6, 10), 0.30000000000000004, 0.4), 9),
            (((5, 2), (6, 10), 0.25, 0.375),((6, 0), (6, 10), 0.4, 0.5), 8),
            (((5, 2), (6, 10), 0.375, 0.75),((6, 0), (6, 10), 0.5, 0.8), 7)]
        """
        end_ribbons = []
        ribbons = self.get_start_ribbons()
        while ribbons:
            new_end_ribbons, new_other_ribbons = self.separate_end_ribbons(ribbons)
            end_ribbons.extend(new_end_ribbons)
            ribbons = [
                next_ribbon
                for ribbon in new_other_ribbons
                for next_ribbon in self.get_next_ribbons(ribbon)
            ]
        return sorted(end_ribbons, key=lambda ribbon: (ribbon.end.start, ribbon.end.end))

    def get_ribbons(self) -> List["Ribbon"]:
        all_ribbons = []
        ribbons = self.get_start_ribbons()
        while ribbons:
            _, new_other_ribbons = self.separate_end_ribbons(ribbons)
            all_ribbons.extend(ribbons)
            ribbons = [
                next_ribbon
                for ribbon in new_other_ribbons
                for next_ribbon in self.get_next_ribbons(ribbon)
            ]
        return sorted(all_ribbons, key=lambda ribbon: (ribbon.end.start, ribbon.end.end))
    
    def separate_end_ribbons(self, ribbons: List["Ribbon"]) -> Tuple[List["Ribbon"], List["Ribbon"]]:
        end_ribbons, other_ribbons = [], []
        for ribbon in ribbons:
            if self.check_is_end_ribbon(ribbon):
                end_ribbons.append(ribbon)
            else:
                other_ribbons.append(ribbon)
        return end_ribbons, other_ribbons

    def filter_end_ribbons(self, ribbons: List["Ribbon"]) -> List["Ribbon"]:
        return list(filter(self.check_is_end_ribbon, ribbons))
    
    def check_is_end_ribbon(self, ribbon: "Ribbon") -> bool:
        return ribbon.ends_on_x(self.mountain.width)
    
    def get_next_ribbons(self, ribbon: "Ribbon") -> List["Ribbon"]:
        next_side_range = self.get_next_side_range_from_ribbon(ribbon)
        if not next_side_range:
            next_ribbons = []
        else:
            next_ribbons = [
                next_ribbon
                for side_range_ribbons in [self.make_ribbons_from_side_range(next_side_range, previous=ribbon)]
                for next_ribbon in side_range_ribbons
            ]
            for next_ribbon in list(next_ribbons):
                if next_ribbon.is_mid_point or almost_equal(next_ribbon.end.start, next_ribbon.end.end):
                    continue
                if almost_equal(next_ribbon.end.start, 0) and almost_equal(next_ribbon.end.side.points[0].x, self.mountain.width):
                    next_ribbons.append(Ribbon(
                        start=next_ribbon.start.replace(end=next_ribbon.start.start),
                        end=next_ribbon.end.replace(end=next_ribbon.end.start),
                        is_mid_point=next_ribbon.is_mid_point,
                        previous=next_ribbon.previous,
                    ))
                elif almost_equal(next_ribbon.end.end, 1) and almost_equal(next_ribbon.end.side.points[1].x, self.mountain.width):
                    next_ribbons.append(Ribbon(
                        start=next_ribbon.start.replace(start=next_ribbon.start.end),
                        end=next_ribbon.end.replace(start=next_ribbon.end.end),
                        is_mid_point=next_ribbon.is_mid_point,
                        previous=next_ribbon.previous,
                    ))
        end_side_is_on_mid_point_at_start = (
           ribbon.end.side == ribbon.end.hill.mid_max_side and almost_equal(ribbon.end.start, 0)
        )
        end_side_is_on_mid_point_at_end = (
           ribbon.end.side == ribbon.end.hill.min_mid_side and almost_equal(ribbon.end.end, 1)
        )
        if end_side_is_on_mid_point_at_start or end_side_is_on_mid_point_at_end:
            next_ribbons.extend(
                Ribbon(
                    start=SideRange(
                        hill=hill,
                        side=hill.min_mid_side,
                        start=1,
                        end=1,
                    ),
                    end=SideRange(
                        hill=hill,
                        side=hill.min_max_side,
                        start=hill.new_factor,
                        end=hill.new_factor,
                    ),
                    is_mid_point=True,
                    previous=ribbon,
                )
                for hill in self.mid_point_hill_map[ribbon.end.hill.mid_point] - {ribbon.end.hill}
            )
        return next_ribbons

    def get_next_side_range_from_ribbon(self, ribbon: "Ribbon") -> Optional["SideRange"]:
        return self.translate_side_range(ribbon.end)

    def translate_side_range(self, side_range: "SideRange") -> Optional["SideRange"]:
        next_hill_and_side = self.hill_side_map.get_from_side_range(side_range)
        if not next_hill_and_side:
            return None
        next_hill, next_side = next_hill_and_side
        start, end = side_range.start, side_range.end
        if side_range.side.points != next_side.points:
            start, end = 1 - end, 1 - start
        return SideRange(hill=next_hill, side=next_side, start=start, end=end)
    
    def get_start_ribbons(self) -> List["Ribbon"]:
        """
        >>> hill = Hill(points=(Point3D(0, 0, 0), Point3D(5, 5, 1), Point3D(0, 10, 2)))
        >>> solver = MountainSolver2.from_mountain( Mountain(hills=[hill], width=5, height=10))
        >>> show_ribbons(solver.get_start_ribbons())
        [(((0, 0), (0, 10), 0, 0.5), ((0, 0), (5, 5), 0.0, 1), 1), (((0, 0), (0, 10), 0.5, 1), ((0, 10), (5, 5), 0, 1.0), 1)]
        
        >>> solver = MountainSolver2.from_mountain(Mountain.from_text(VIABLE_EXAMPLE_INPUT_3))
        >>> show_ribbons(solver.get_start_ribbons())
        [(((0, 0), (0, 10), 0, 0.7), ((0, 0), (1, 5), 0.0, 1), 1),
            (((0, 0), (0, 10), 0.7, 1), ((0, 10), (1, 5), 0, 1.0), 1)]
        """
        start_side_ranges = self.get_start_side_ranges()
        ribbons = [
            ribbon
            for side_range in start_side_ranges
            for ribbon in self.make_ribbons_from_side_range(side_range)
        ]
        ribbons += self.get_edge_to_edge_ribbons(start_side_ranges, self.mountain.width, reverse_sides=False)
        ribbons += self.get_edge_to_edge_ribbons(self.get_side_ranges_on(self.mountain.width), 0, reverse_sides=True)
        return ribbons

    def get_edge_to_edge_ribbons(self, side_ranges: List["SideRange"], end_x: float, reverse_sides: bool = False) -> List["Ribbon"]:
        ribbons = []
        for side_range in side_ranges:
            hill = side_range.hill
            if side_range.side != hill.min_max_side:
                continue
            if not almost_equal(hill.mid_point.x, end_x):
                continue
            start = side_range.replace(start=hill.new_factor, end=hill.new_factor)
            end = SideRange(hill=hill, side=hill.min_mid_side, start=1, end=1)
            if reverse_sides:
                start, end = end, start
            ribbons.append(Ribbon(
                start=start,
                end=end,
                is_mid_point=False,
                previous=None,
            ))
        return ribbons
    
    def make_ribbons_from_side_range(self, side_range: "SideRange", previous: Optional["Ribbon"] = None) -> List["Ribbon"]:
        """
        >>> hill = Hill(points=(Point3D(0, 0, 0), Point3D(5, 5, 1), Point3D(0, 10, 2)))
        >>> solver = MountainSolver2.from_mountain( Mountain(hills=[hill], width=5, height=10))
        >>> show_ribbons(solver.make_ribbons_from_side_range(SideRange(hill=hill, side=hill.min_mid_side, start=0, end=1)))
        [(((0, 0), (5, 5), 0, 1), ((0, 0), (0, 10), 0.0, 0.5), 1)]
        >>> show_ribbons(solver.make_ribbons_from_side_range(SideRange(hill=hill, side=hill.mid_max_side, start=0, end=1)))
        [(((0, 10), (5, 5), 0, 1), ((0, 0), (0, 10), 0.5, 1.0), 1)]
        >>> show_ribbons(solver.make_ribbons_from_side_range(SideRange(hill=hill, side=hill.min_max_side, start=0, end=1)))
        [(((0, 0), (0, 10), 0, 0.5), ((0, 0), (5, 5), 0.0, 1), 1), (((0, 0), (0, 10), 0.5, 1), ((0, 10), (5, 5), 0, 1.0), 1)]
        """
        next_side_ranges = self.get_next_side_ranges(side_range)
        if len(next_side_ranges) == 2:
            split_side_ranges = [
                side_range.replace(end=side_range.hill.new_factor),
                side_range.replace(start=side_range.hill.new_factor),
            ]
        else:
            split_side_ranges = [side_range]
        return [
            Ribbon(start=split_side_range, end=next_side_range, is_mid_point=False, previous=previous)
            for split_side_range, next_side_range in zip(split_side_ranges, next_side_ranges)
            if not previous or (split_side_range.hill not in previous.seen_hills)
        ]
    
    def get_next_side_ranges(self, side_range: "SideRange", prefer_min_mid_for_new_factor: bool = True) -> List["SideRange"]:
        """
        >>> hill = Hill(points=(Point3D(0, 0, 0), Point3D(5, 5, 1), Point3D(0, 10, 2)))
        >>> solver = MountainSolver2.from_mountain( Mountain(hills=[hill], width=5, height=10))
        >>> show_side_ranges(solver.get_next_side_ranges(SideRange(hill=hill, side=hill.min_mid_side, start=0, end=1)))
        [((0, 0), (0, 10), 0.0, 0.5)]
        >>> show_side_ranges(solver.get_next_side_ranges(SideRange(hill=hill, side=hill.mid_max_side, start=0, end=1)))
        [((0, 0), (0, 10), 0.5, 1.0)]
        >>> show_side_ranges(solver.get_next_side_ranges(SideRange(hill=hill, side=hill.min_max_side, start=0, end=1)))
        [((0, 0), (5, 5), 0.0, 1), ((0, 10), (5, 5), 0, 1.0)]
        """
        hill = side_range.hill
        side = side_range.side
        start = side_range.start
        end = side_range.end
        new_factor = hill.new_factor
        if side == hill.min_mid_side:
            return [
                SideRange(
                    hill=hill,
                    side=hill.min_max_side,
                    start=start * new_factor,
                    end=end * new_factor,
                ),
            ]
        if side == hill.mid_max_side:
            return [
                SideRange(
                    hill=hill,
                    side=hill.min_max_side,
                    start=new_factor + start * (1 - new_factor),
                    end=new_factor + end * (1 - new_factor),
                ),
            ]
        if side != hill.min_max_side:
            raise Exception(f"Side {side} was not one of the hill's sides {hill.sides}")
        if almost_less_equal(end, new_factor):
            # Give the option to the caller to keep the same side when restricting to make checks simpler
            if prefer_min_mid_for_new_factor or not almost_equal(start, end):
                return [
                    SideRange(
                        hill=hill,
                        side=hill.min_mid_side,
                        start=start / new_factor,
                        end=end / new_factor,
                    ),
                ]
        if almost_less_equal(new_factor, start):
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
    
    def get_start_side_ranges(self) -> List["SideRange"]:
        """
        >>> show_side_ranges(MountainSolver2.from_mountain(Mountain.from_text(VIABLE_EXAMPLE_INPUT_3)).get_start_side_ranges())
        [((0, 0), (0, 10), 0, 1)]
        """
        return self.get_side_ranges_on(0)

    def get_side_ranges_on(self, x: float) -> List["SideRange"]:
        side_ranges = []
        for hill in self.mountain.hills:
            sides = [side for side in hill.sides if side.is_on_x(x)]
            if not sides:
                continue
            side, = sides
            side_ranges.append(SideRange.from_hill_and_side(hill, side))
        return side_ranges


@dataclass(frozen=True)
class Ribbon:
    start: "SideRange"
    end: "SideRange"
    is_mid_point: bool
    previous: Optional["Ribbon"]

    @cached_property
    def length(self) -> int:
        length = 0
        node = self
        while node:
            length += 1
            node = node.previous
        return length
    
    def __str__(self) -> str:
        result = f" * Ribbon{'(midpoint)' if self.is_mid_point else ''}:\n"
        if self.start.hill == self.end.hill:
            start_hill_point_names = end_hill_point_names = {
                self.start.hill.min_point: 'min',
                self.start.hill.mid_point: 'mid',
                self.start.hill.max_point: 'max',
            }
            result += f"   * Hill: {', '.join(f'{name}: ({p.x},{p.y},{p.z})' for p, name in start_hill_point_names.items())}, new factor: {self.start.hill.new_factor}\n"
        else:
            result += f"   * !Hills differ!"
            start_hill_point_names = {
                self.start.hill.min_point: 'min',
                self.start.hill.mid_point: 'mid',
                self.start.hill.max_point: 'max',
            }
            end_hill_point_names = {
                self.end.hill.min_point: 'min',
                self.end.hill.mid_point: 'mid',
                self.end.hill.max_point: 'max',
            }
        result += f"   * Start:\n"
        if self.start.hill != self.end.hill:
            result += f"     * Hill: {', '.join(f'{name}: ({p.x},{p.y},{p.z})' for p, name in start_hill_point_names.items())}, new factor: {self.start.hill.new_factor}\n"
        result += (
            f"     * Side: {self.start.start}-{self.start.end} {', '.join(f'({p.x},{p.y},{p.z}) ' + start_hill_point_names.get(p, 'N/A') for p in self.start.side.points)}\n"
            f"   * End:\n"
        )
        if self.start.hill != self.end.hill:
            result += f"     * Hill: {', '.join(f'{name}: ({p.x},{p.y},{p.z})' for p, name in end_hill_point_names.items())}, new factor: {self.end.hill.new_factor}\n"
        result += f"     * Side: {self.end.start}-{self.end.end} {', '.join(f'({p.x},{p.y},{p.z}) ' + end_hill_point_names.get(p, 'N/A') for p in self.end.side.points)}\n"
        return result + (str(self.previous) if self.previous else '')

    @cached_property
    def seen_hills(self) -> Set["Hill"]:
        seen_hills = {self.start.hill}
        if self.previous:
            seen_hills |= self.previous.seen_hills
        return seen_hills

    def ends_on_x(self, x: float) -> bool:
        # if self.is_mid_point:
        #     print(f"{self.end.start}-{self.end.end}, {self.end.side.points[0].x}-{self.end.side.points[1].x} ?= {x}", self)
        if almost_equal(self.end.start, self.end.end) and ((almost_equal(self.end.start, 0) and almost_equal(self.end.side.points[0].x, x)) or (almost_equal(self.end.end, 1) and almost_equal(self.end.side.points[1].x, x))):
            return True
        return self.end.is_on_x(x)

    def get_points(self) -> List[Point3D]:
        return [
            *self.start.get_points(),
            *self.end.get_points()[::-1],
        ]

    def get_points_history(self) -> List[List[Point3D]]:
        points_history = []
        for node in self.iterate_history():
            points_history.append(node.get_points())
        return points_history[::-1]

    def iterate_history(self) -> Iterable["Ribbon"]:
        node = self
        while node:
            yield node
            node = node.previous

    def total_history_length_range(self) -> Tuple[float, float]:
        start_length = 0.0
        end_length = 0.0
        for node in self.iterate_history():
            node_start_length, node_end_length = node.get_length_range()
            start_length += node_start_length
            end_length += node_end_length
        min_length, max_length = sorted([start_length, end_length])
        return min_length, max_length

    def get_length_range(self) -> Tuple[float, float]:
        start_start, start_end = self.start.get_points()
        end_start, end_end = self.end.get_points()
        start_length = start_start.distance(end_start)
        end_length = start_end.distance(end_end)
        return start_length, end_length


@dataclass
class MountainSolver:
    mountain: "Mountain"
    hill_side_map: "HillSideMap"

    @classmethod
    def from_mountain(cls, mountain: "Mountain") -> "MountainSolver":
        return cls(mountain=mountain, hill_side_map=HillSideMap.from_mountain(mountain))
    
    def get_viable_ys(self, viable_side_ranges: Optional[List["SideRange"]] = None) -> List[Tuple[float, float]]:
        """
        >>> Mountain.from_text(VIABLE_EXAMPLE_INPUT_1).get_solver().get_viable_ys()
        [(3.0, 6.0)]
        >>> Mountain.from_text(VIABLE_EXAMPLE_INPUT_2).get_solver().get_viable_ys()
        [(0.0, 0.8...)]
        """
        if viable_side_ranges is None:
            viable_side_ranges = self.get_all_viable_side_ranges()
        y_ranges = sorted(
            side_range.get_y_range()
            for side_range in viable_side_ranges
        )
        merged_y_ranges = []
        previous_y_range = None
        for y_range in y_ranges:
            if previous_y_range is None:
                previous_y_range = y_range
                continue
            if y_range[0] > previous_y_range[1] and not almost_equal(y_range[0], previous_y_range[1]):
                merged_y_ranges.append(previous_y_range)
                previous_y_range = y_range
                continue
            previous_y_range = previous_y_range[0], y_range[1]
        if previous_y_range:
            merged_y_ranges.append(previous_y_range)
        return merged_y_ranges

    def get_all_viable_side_ranges(self):
        first_side_ranges = self.get_first_side_ranges()
        side_ranges = self.get_all_side_ranges(first_side_ranges)
        end_ranges = self.get_all_end_side_ranges(side_ranges)
        reverse_side_ranges = self.get_all_side_ranges(end_ranges)
        reverse_end_side_ranges = self.get_all_end_side_ranges(reverse_side_ranges, match_x=0)
        merged_side_ranges = self.merge_side_ranges(reverse_end_side_ranges)
        # print(f"{len(first_side_ranges)} first side ranges")
        # print(f"{len(side_ranges)} side ranges")
        # print(f" * {', '.join(map(str, (self.mountain.hills.index(side_range.hill) for side_range in side_ranges)))}")
        # print(f"{len(end_ranges)} end side ranges")
        # print(f"{len(reverse_side_ranges)} reverse side ranges")
        # print(f"{len(reverse_end_side_ranges)} reverse end side ranges")
        # print(f"{len(merged_side_ranges)} merged side ranges")
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
                    if side_range.start > previous.end and not almost_equal(side_range.start, previous.end):
                        merged_side_ranges.append(previous)
                        previous = side_range
                        continue
                    previous = previous.replace(end=side_range.end)
                if previous:
                    merged_side_ranges.append(previous)
        merged_side_ranges.sort(key=lambda _side_range: _side_range.min_y)
        return merged_side_ranges

    def get_all_end_side_ranges(self, all_side_ranges: Optional[List["SideRange"]] = None, match_x: int = None) -> List["SideRange"]:
        """
        >>> show_side_ranges(Mountain.from_text(VIABLE_EXAMPLE_INPUT_1).get_solver().get_all_end_side_ranges())
        [((0, 0), (6, 0), 1, 1), ((6, 0), (6, 6), 0, 0.4999...)]
        >>> show_side_ranges(Mountain.from_text(VIABLE_EXAMPLE_INPUT_2).get_solver().get_all_end_side_ranges())
        [((10, 0), (10, 6), 0..., 0...)]
        """
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
        """
        >>> show_side_ranges(Mountain.from_text(VIABLE_EXAMPLE_INPUT_1).get_solver().get_all_side_ranges())
        [...((6, 0), (6, 6), 0, 0.4999...)...]
        >>> show_side_ranges(Mountain.from_text(VIABLE_EXAMPLE_INPUT_2).get_solver().get_all_side_ranges())
        [...((10, 0), (10, 6), 0..., 0...)...]
        >>> solver = Mountain.from_text(VIABLE_EXAMPLE_INPUT_2).get_solver()
        >>> show_side_ranges(solver.get_all_side_ranges(solver.get_all_end_side_ranges()))
        [...((0, 0), (0, 6), 0..., 1.0)...]
        """
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
        >>> solver = Mountain.from_text(VIABLE_EXAMPLE_INPUT_1).get_solver()
        >>> first_side_ranges = solver.get_first_side_ranges()
        >>> second_side_ranges_and_seen, second_terminals = solver.get_next_side_ranges_and_seen([
        ...     (_side_range, {_side_range.hill}) for _side_range in first_side_ranges])
        >>> show_side_ranges(_side_range for _side_range, _ in second_side_ranges_and_seen)
        [((0, 0), (6, 6), 0.0, ...)]
        >>> show_side_ranges(second_terminals)
        []
        >>> third_side_ranges_and_seen, third_terminals = solver.get_next_side_ranges_and_seen([
        ...     (_side_range, {_side_range.hill}) for _side_range, _ in second_side_ranges_and_seen])
        >>> show_side_ranges(_side_range for _side_range, _ in third_side_ranges_and_seen)
        []
        >>> show_side_ranges(third_terminals)
        [((0, 0), (6, 0), 0.0, 1), ((6, 0), (6, 6), 0, ...)]

        >>> solver = Mountain.from_text(VIABLE_EXAMPLE_INPUT_2).get_solver()
        >>> first_side_ranges = solver.get_first_side_ranges()
        >>> second_side_ranges_and_seen, second_terminals = solver.get_next_side_ranges_and_seen([
        ...     (_side_range, {_side_range.hill}) for _side_range in first_side_ranges])
        >>> show_side_ranges(_side_range for _side_range, _ in second_side_ranges_and_seen)
        [((0, 6), (4, 3), 0.0, ...)]
        >>> show_side_ranges(second_terminals)
        []
        >>> third_side_ranges_and_seen, third_terminals = solver.get_next_side_ranges_and_seen([
        ...     (_side_range, {_side_range.hill}) for _side_range, _ in second_side_ranges_and_seen])
        >>> show_side_ranges(_side_range for _side_range, _ in third_side_ranges_and_seen)
        [((2, 6), (4, 3), 0, ...)]
        >>> show_side_ranges(third_terminals)
        [((0, 6), (2, 6), 0.0, 1)]
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
        ...     Mountain.from_text(VIABLE_EXAMPLE_INPUT_1).get_solver().get_first_side_ranges())
        [((0, 0), (0, 6), 0, 1)]

        >>> show_side_ranges(
        ...     Mountain.from_text(VIABLE_EXAMPLE_INPUT_2).get_solver().get_first_side_ranges())
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
        >>> solver = Mountain.from_text(VIABLE_EXAMPLE_INPUT_2).get_solver()
        >>> first_side_ranges = solver.get_first_side_ranges()
        >>> second_side_ranges = [
        ...     solver.translate_side_range_to_next_triangle(next_side_range)
        ...     for _side_range in first_side_ranges
        ...     for next_side_range in solver.get_next_side_ranges(_side_range)
        ... ]

        >>> solver = Mountain.from_text(VIABLE_EXAMPLE_INPUT_2).get_solver()
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
        >>> solver = Mountain.from_text(VIABLE_EXAMPLE_INPUT_1).get_solver()
        >>> first_side_ranges = solver.get_first_side_ranges()
        >>> second_side_ranges = [
        ...     next_side_range
        ...     for _side_range in first_side_ranges
        ...     for next_side_range in solver.get_next_side_ranges(_side_range)
        ... ]
        >>> show_side_ranges(second_side_ranges)
        [((0, 0), (6, 6), 0.0, ...)]

        >>> solver = Mountain.from_text(VIABLE_EXAMPLE_INPUT_2).get_solver()
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
        first_equals = almost_equal(self.side.points[0].x, match_x)
        second_equals = almost_equal(self.side.points[1].x, match_x)
        if first_equals and second_equals:
            return self
        if first_equals and almost_equal(self.start, 0):
            return self.replace(end=0)
        if second_equals and almost_equal(self.end, 1):
            return self.replace(start=1)
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
    
    def is_on_x(self, x: float) -> bool:
        return self.side.is_on_x(x)
    
    def get_points(self) -> List[Point3D]:
        first = self.side.points[0]
        second = self.side.points[1]
        return [
            Point3D(
                first.x + (second.x - first.x) * factor,
                first.y + (second.y - first.y) * factor,
                first.z + (second.z - first.z) * factor,
            )
            for factor in [self.start, self.end]
        ]


DefaultDelta = 0.000001


def almost_equal(left: float, right: float, delta: float = DefaultDelta) -> bool:
    return abs(left - right) <= delta


def almost_greater(left: float, right: float, delta: float = DefaultDelta) -> bool:
    return left > right and not almost_equal(left, right, delta=delta)


def almost_greater_equal(left: float, right: float, delta: float = DefaultDelta) -> bool:
    return left >= right or almost_equal(left, right, delta=delta)


def almost_less(left: float, right: float, delta: float = DefaultDelta) -> bool:
    return left < right and not almost_equal(left, right, delta=delta)


def almost_less_equal(left: float, right: float, delta: float = DefaultDelta) -> bool:
    return left <= right or almost_equal(left, right, delta=delta)


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
        # print({mountain.hills.index(hill): {(key[0][:2], key[1][:2]): mountain.hills.index(other_hill) for key, (other_hill, _) in side_map.items()} for hill, side_map in side_map.items()})
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
        # print({(key[0][:2], key[1][:2]): {mountain.hills.index(hill) for hill in hills} for key, hills in by_side_key.items()})
        return cls(by_side_key=by_side_key)

    def __getitem__(self, item: "Side") -> Set["Hill"]:
        return self.by_side_key[item.key]


@dataclass
class MidPointHillMap:
    by_point: Dict[Point3D, Set["Hill"]]

    @classmethod
    def from_mountain(cls, mountain: "Mountain") -> "MidPointHillMap":
        by_point = {}
        for hill in mountain.hills:
            by_point.setdefault(hill.mid_point, set()).add(hill)
        return cls(by_point=by_point)
    
    def __getitem__(self, item: "Point3D") -> Set["Hill"]:
        return self.by_point.get(item, set())


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
        """
        >>> hill = Hill(points=(Point3D(0, 0, 0), Point3D(5, 5, 1), Point3D(0, 10, 2)))
        >>> hill.four_points_and_factor
        (Point3D(x=0, y=0, z=0), Point3D(x=5, y=5, z=1), Point3D(x=0, y=10, z=2), 0.5)
        >>> hill = Hill(points=tuple(reversed((Point3D(0, 0, 0), Point3D(5, 5, 1), Point3D(0, 10, 2)))))
        >>> hill.four_points_and_factor
        (Point3D(x=0, y=0, z=0), Point3D(x=5, y=5, z=1), Point3D(x=0, y=10, z=2), 0.5)
        """
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
        """
        >>> hill = Hill(points=[Point3D(0, 0, 0), Point3D(5, 5, 1), Point3D(0, 10, 2)])
        >>> hill.min_mid_side
        Side(points=(Point3D(x=0, y=0, z=0), Point3D(x=5, y=5, z=1)), ...)
        >>> hill.mid_max_side
        Side(points=(Point3D(x=5, y=5, z=1), Point3D(0, 10, 2)), ...)
        >>> hill.min_max_side
        Side(points=(Point3D(x=0, y=0, z=0), Point3D(0, 10, 2)), ...)
        """
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
            almost_equal(self.points[0].x, x)
            and almost_equal(self.points[1].x, x)
        )

    @cached_property
    def min_y(self) -> float:
        return min(self.points[0].y, self.points[1].y)


VIABLE_EXAMPLE_INPUT_1 = """
6 6 4 2
0 0 1
6 0 2
6 6 4
0 6 3
1 2 3
1 3 4
"""


VIABLE_EXAMPLE_INPUT_2 = """
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

VIABLE_EXAMPLE_INPUT_3 = """
6 10 10 12
0 0 0
1 5 7
0 10 10
2 5 5
3 0 1
3 10 11
4 5 6
6 0 2
5 2 4
6 10 12
1 2 3
1 4 2
2 4 3
3 4 6
4 7 6
6 7 10
7 9 10
10 9 8
5 8 9
9 7 5
4 5 7
5 4 1
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


def show_ribbons(ribbons: List[Optional["Ribbon"]]) -> List[Optional[Tuple]]:
    return list(map(show_ribbon, ribbons))


def show_ribbon(ribbon: Optional["Ribbon"]) -> Optional[Tuple]:
    if not ribbon:
        return None
    return (show_side_range(ribbon.start), show_side_range(ribbon.end), ribbon.length)


Challenge.main()
challenge = Challenge()
