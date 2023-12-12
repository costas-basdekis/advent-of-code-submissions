#!/usr/bin/env python3
from dataclasses import dataclass
import re
from functools import cached_property
from itertools import count, groupby
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

import click

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples, Direction8
from year_2023.day_21 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        636391426712747
        """
        return (GardenExtended.from_map_text(_input)
                .get_generator(1000, debugger=debugger)
                .get_reachable_tile_count(26501365))

    def play(self):
        context = PlayContext.from_input_garden_text(self.input)
        re_switch = re.compile(r"^s([TI])$")
        re_move = re.compile(r"^m(\d+)$")
        re_values = re.compile(r"^v(-?\d+),(-?\d+)$")
        re_origin_offsets = re.compile(r"^oo(-?\d+),(-?\d+)$")
        re_extension_offsets = re.compile(r"^eo(-?\d+),(-?\d+)(?:([LCR])([TCB]))?$")
        re_extension_count = re.compile(r"^ec(-?\d+),(-?\d+)$")
        re_print = re.compile(r"^p$")
        re_visualise_extension_offsets = re.compile(r"^veo$")
        re_visualise_extension_differences = re.compile(r"^ved$")
        re_visualise_extension_counts = re.compile(r"^vec$")
        re_check_extension_boundaries = re.compile(r"^ce$")
        re_check_generator_map = re.compile(r"^cgm$")
        re_check_generator_counts = re.compile(r"^cgc$")
        re_check_generator_max_size = re.compile(r"^cgms$")
        def c(text: any) -> str:
            return click.style(str(text), fg="red")
        def g(text: any) -> str:
            return click.style(str(text), fg="green")
        while True:
            print(f"Garden '{g(context.garden_name)}' at {g(context.step_count)} steps")
            user_input = click.prompt((
                f"Switch to garden {c('sX')}, "
                f"move to {c('mX')}, "
                f"show values for {c('vX,X')}, "
                f"show origin offsets for {c('ooX,X')}, "
                f"show extension offsets for {c('eoX,X')}, "
                f"show extension count for {c('ecX,X')}, "
                f"{c('p')} to print, "
                f"{c('veo')} to visualise extension offsets, "
                f"{c('ved')} to visualise extension differences, "
                f"{c('vec')} to visualise extension counts, "
                f"{c('ce')} to check extension boundaries, "
                f"{c('cgm')} to check generator map, "
                f"{c('cgc')} to check generator counts, "
                f"or {c('cgms')} to check generator max size"
            ), default=f"m{context.step_count + 1}")
            if match := re_switch.match(user_input):
                garden_letter = match.groups()[0]
                garden_name = {"T": "test", "I": "input"}[garden_letter]
                context = context.switch_to(garden_name)
            elif match := re_move.match(user_input):
                context = context.to_step_count(int(match.groups()[0]))
            elif match := re_values.match(user_input):
                offset_point = Point2D(int(match.groups()[0]), int(match.groups()[1]))
                offset = Point2D(offset_point.x * context.garden.width, offset_point.y * context.garden.height)
                print(f"Showing values for {offset_point}")
                extension_counts = {
                    point: (
                        str(context.first_tile_step_count_map[extension_point])
                        if extension_point in context.first_tile_step_count_map else
                        click.style("?", fg="red")
                    )
                    for x in range(context.garden.width)
                    for y in range(context.garden.height)
                    for point in [Point2D(x, y)]
                    for extension_point in [point.offset(offset)]
                    if extension_point in context.garden
                }
                print(f"Offsets for {offset_point} ({set(map(click.unstyle, extension_counts.values()))}):")
                print(self.show_garden_string_table(context.garden, extension_counts))
            elif match := re_origin_offsets.match(user_input):
                offset_point = Point2D(int(match.groups()[0]), int(match.groups()[1]))
                offset = Point2D(offset_point.x * context.garden.width, offset_point.y * context.garden.height)
                print(f"Showing origin offsets for {offset_point}")
                origin_counts = {
                    point: context.first_tile_step_count_map[point]
                    for x in range(context.garden.width)
                    for y in range(context.garden.height)
                    for point in [Point2D(x, y)]
                    if point in context.first_tile_step_count_map
                }
                extension_counts = {
                    point: context.first_tile_step_count_map[extension_point]
                    for point in origin_counts
                    for extension_point in [point.offset(offset)]
                    if extension_point in context.first_tile_step_count_map
                }
                extension_offsets = {
                    point: (
                        str(extension_counts[point] - origin_counts[point])
                        if point in extension_counts else
                        "X"
                    )
                    for point in origin_counts
                }
                print(f"Origin offsets for {offset_point} ({set(map(click.unstyle, extension_offsets.values()))}):")
                print(self.show_garden_string_table(context.garden, extension_offsets))
            elif match := re_extension_offsets.match(user_input):
                offset_point = Point2D(int(match.groups()[0]), int(match.groups()[1]))
                extension_offsets = self.get_extension_offset_texts(context.garden, context.first_tile_step_count_map, offset_point,
                                                                    horizontal_bias=match.groups()[2],
                                                                    vertical_bias=match.groups()[3])
                print(f"Extension offsets for {offset_point} ({set(map(click.unstyle, extension_offsets.values()))}):")
                print(self.show_garden_string_table(context.garden, extension_offsets))
            elif match := re_extension_count.match(user_input):
                offset_point = Point2D(int(match.groups()[0]), int(match.groups()[1]))
                extension_tiles = context.garden.get_extension_reachable_tiles(context.step_count, context.first_tile_step_count_map, offset_point)
                tile_strings = {
                    point: (
                        "O"
                        if point in extension_tiles else
                        "."
                    )
                    for point in context.garden.plots
                }
                print(f"Extension count for {offset_point} ({len(extension_tiles)}):")
                print(self.show_string_table(tile_strings))
            elif re_print.match(user_input):
                print(context.garden.show_with_other_tiles(context.other_tiles, show_start=True, show_extensions=True))
            elif re_visualise_extension_offsets.match(user_input):
                extension_texts = {
                    offset_point: self.show_garden_string_table(context.garden, self.get_extension_offset_texts(context.garden,
                                                                                                        context.first_tile_step_count_map,
                                                                                                        offset_point))
                    for offset_point in context.offset_points
                }
                extension_ids = self.convert_table_to_ids(extension_texts)
                extension_ids = self.colour_table(extension_ids)
                if Point2D(0, 0) in extension_ids:
                    extension_ids[Point2D(0, 0)] = click.style(extension_ids[Point2D(0, 0)], fg="green")
                print(self.show_string_table(extension_ids))
            elif re_visualise_extension_differences.match(user_input):
                extension_texts = {
                    offset_point: self.show_garden_string_table(context.garden, self.get_extension_difference_texts(context.garden,
                                                                                                        context.first_tile_step_count_map,
                                                                                                        offset_point))
                    for offset_point in context.offset_points
                }
                extension_ids = self.convert_table_to_ids(extension_texts)
                extension_ids = self.colour_table(extension_ids)
                if extension_ids:
                    extension_ids[Point2D(0, 0)] = click.style(extension_ids[Point2D(0, 0)], fg="green")
                print(self.show_string_table(extension_ids))
            elif re_visualise_extension_counts.match(user_input):
                counts = {
                    offset_point: context.garden.get_extension_reachable_tiles(context.step_count, context.first_tile_step_count_map, offset_point)
                    for offset_point in context.offset_points
                }
                counts_strings = {
                    point: str(len(_count))
                    for point, _count in counts.items()
                    if _count
                }
                counts_strings = self.colour_table(counts_strings)
                if counts_strings:
                    counts_strings[Point2D(0, 0)] = click.style(counts_strings[Point2D(0, 0)], fg="green")
                print(self.show_string_table(counts_strings))
            elif re_check_extension_boundaries.match(user_input):
                matches = set()
                mismatches = set()
                for offset_point in context.offset_points:
                    if offset_point.x == offset_point.y == 0:
                        continue
                    offset = Point2D(offset_point.x * context.garden.width, offset_point.y * context.garden.height)
                    if offset_point.x > 0:
                        for y in range(context.garden.height):
                            extension_point = Point2D(0, y).offset(offset)
                            previous_point = extension_point.offset(Point2D(-1, 0))
                            if extension_point not in context.first_tile_step_count_map:
                                continue
                            if context.first_tile_step_count_map[extension_point] == context.first_tile_step_count_map[previous_point] + 1:
                                matches.add(extension_point)
                            else:
                                mismatches.add(extension_point)
                    elif offset_point.x < 0:
                        for y in range(context.garden.height):
                            extension_point = Point2D(context.garden.width - 1, y).offset(offset)
                            previous_point = extension_point.offset(Point2D(1, 0))
                            if extension_point not in context.first_tile_step_count_map:
                                continue
                            if context.first_tile_step_count_map[extension_point] == context.first_tile_step_count_map[previous_point] + 1:
                                matches.add(extension_point)
                            else:
                                mismatches.add(extension_point)
                    if offset_point.y > 0:
                        for x in range(context.garden.width):
                            extension_point = Point2D(x, 0).offset(offset)
                            previous_point = extension_point.offset(Point2D(0, -1))
                            if extension_point not in context.first_tile_step_count_map:
                                continue
                            if context.first_tile_step_count_map[extension_point] == context.first_tile_step_count_map[previous_point] + 1:
                                matches.add(extension_point)
                            else:
                                mismatches.add(extension_point)
                    elif offset_point.y < 0:
                        for x in range(context.garden.width):
                            extension_point = Point2D(x, context.garden.height - 1).offset(offset)
                            previous_point = extension_point.offset(Point2D(0, 1))
                            if extension_point not in context.first_tile_step_count_map:
                                continue
                            if context.first_tile_step_count_map[extension_point] == context.first_tile_step_count_map[previous_point] + 1:
                                matches.add(extension_point)
                            else:
                                mismatches.add(extension_point)
                print(context.garden.show_with_other_tiles(context.other_tiles, show_start=True, show_extensions=True, matches_and_mismatches=(matches, mismatches)))
                print(f"There were {len(matches)} matches and {len(mismatches)} mismatches")
            elif re_check_generator_map.match(user_input):
                match_map = {}
                match_count = 0
                mismatch_count = 0
                first_map_mismatch_tuple: Optional[Tuple[Point2D, Dict[Point2D, int], Dict[Point2D, int]]] = None
                for offset_point in context.offset_points:
                    actual_extension = context.garden.get_extension(context.first_tile_step_count_map, offset_point)
                    try:
                        generated_extension = context.generator.get_extension(offset_point)
                    except NotImplementedError:
                        match_map[offset_point] = ""
                        continue
                    matches = all(
                        actual_value == generated_extension.get(point)
                        for point, actual_value in actual_extension.items()
                    )
                    match_map[offset_point] = click.style("Y", fg="green") if matches else click.style("N", fg="red")
                    if matches:
                        match_count += 1
                    else:
                        mismatch_count += 1
                        if not first_map_mismatch_tuple:
                            first_map_mismatch_tuple = offset_point, actual_extension, generated_extension
                print(self.show_string_table(match_map))
                print(f"There were {match_count} matches and {mismatch_count} mismatches")
                if first_map_mismatch_tuple:
                    offset_point, actual_extension, generated_extension = first_map_mismatch_tuple
                    diff = {
                        point: (
                            click.style("0", fg="green")
                            if actual_value == generated_value else
                            click.style(str(generated_value - actual_value), fg="red")
                            if generated_value is not None else
                            click.style("M", fg="magenta")
                        )
                        for point, actual_value in actual_extension.items()
                        for generated_value in [generated_extension.get(point)]
                    }
                    print(f"First mismatch at {offset_point}")
                    print(f"Actual (starting at {min(actual_extension)}):")
                    print(self.show_string_table(self.make_diff_table(actual_extension, generated_extension)))
                    print(f"Generated (starting at {min(generated_extension)}):")
                    print(self.show_string_table(self.make_diff_table(generated_extension, actual_extension)))
                    print("Diff:")
                    print(self.show_string_table(diff))
            elif re_check_generator_counts.match(user_input):
                match_map = {}
                match_count = 0
                mismatch_count = 0
                first_count_mismatch_tuple: Optional[Tuple[Point2D, Set[Point2D], Set[Point2D]]] = None
                for offset_point in context.offset_points:
                    actual_extension_count = context.garden.get_extension_reachable_tile_count(context.step_count, context.first_tile_step_count_map, offset_point)
                    generated_extension_count = context.generator.get_extension_reachable_tile_count(context.step_count, offset_point)
                    matches = actual_extension_count == generated_extension_count
                    match_map[offset_point] = click.style("Y", fg="green") if matches else click.style("N", fg="red")
                    if matches:
                        match_count += 1
                    else:
                        mismatch_count += 1
                        if not first_count_mismatch_tuple:
                            first_count_mismatch_tuple = (
                                offset_point,
                                context.garden.get_extension_reachable_tiles(context.step_count, context.first_tile_step_count_map, Point2D(x, y)),
                                context.generator.get_extension_reachable_tiles(context.step_count, offset_point),
                            )
                print(self.show_string_table(match_map))
                print(f"There were {match_count} matches and {mismatch_count} mismatches")
                if first_count_mismatch_tuple:
                    offset_point, actual_extension_tiles, generated_extension_tiles = first_count_mismatch_tuple
                    diff = {
                        point: click.style((
                            "O"
                            if point in actual_extension_tiles else
                            "."
                        ), fg=(
                            "green"
                            if (point in actual_extension_tiles) == (point in generated_extension_tiles) else
                            "red"
                        ))
                        for point in actual_extension_tiles
                    }
                    print(f"First mismatch at {offset_point}")
                    print("Diff:")
                    print(self.show_string_table(diff))
                actual_count = len(context.other_tiles)
                generated_count = context.generator.get_reachable_tile_count(context.step_count)
                print(
                    f"Actual count is {actual_count} "
                    f"vs generated {click.style(str(generated_count), fg=('green' if actual_count == generated_count else 'red'))}")
            elif re_check_generator_max_size.match(user_input):
                max_x, max_y = context.generator.get_max_size_for_steps(context.step_count)
                print(f"There are {context.extension_count.x}x{context.extension_count.y} extensions")
                print(f"Expecting {2 * max_x + 1}x{2 * max_y + 1} extensions")
            else:
                print(f"Cannot parse '{user_input}'")

    def show_garden_string_table(self, garden: "GardenExtended", table: Dict[Point2D, str]) -> str:
        return self.show_string_table(table, (range(garden.width), range(garden.height)))

    def show_string_table(self, table: Dict[Point2D, str], ranges: Optional[Tuple[range, range]] = None) -> str:
        if not table:
            return ""
        if not ranges:
            (min_x, min_y), (max_x, max_y) = min_and_max_tuples(table)
            ranges = (range(min_x, max_x + 1), range(min_y, max_y + 1))
        max_length = max(map(len, map(lambda text: click.unstyle(text), table.values()))) if table else 0
        def rjust_styled(text: str) -> str:
            unstyled = click.unstyle(text)
            justified = unstyled.rjust(max_length)
            if text != unstyled:
                styled = justified.replace(unstyled, text)
            else:
                styled = justified
            return styled
        return "\n".join(
            " ".join(
                rjust_styled(table.get(point, ""))
                for x in ranges[0]
                for point in [Point2D(x, y)]
            )
            for y in ranges[1]
        )

    def convert_table_to_ids(self, table: Dict[Point2D, str]) -> Dict[Point2D, str]:
        id_by_text = {}
        ids_by_point = {
            offset_point: str(id_by_text.setdefault(extension_text, len(id_by_text) + 1))
            for offset_point, extension_text in table.items()
            if extension_text.strip()
        }
        return ids_by_point

    def colour_table(self, table: Dict[Point2D, str]) -> Dict[Point2D, str]:
        colours = [
            "red", "green", "yellow", "blue", "magenta", "cyan",
            "bright_red", "bright_green", "bright_yellow", "bright_blue", "bright_magenta", "bright_cyan",
        ]
        item_counts = {
            item: len(list(items))
            for item, items in groupby(sorted(table.values()))
        }
        recurring_items = [
            item
            for item, _count in item_counts.items()
            if _count > 1
        ]
        recurring_item_colours = {
            item: colours[index % len(colours)]
            for index, item in enumerate(recurring_items)
        }
        coloured_table = {
            offset_point: (
                click.style(item, bg=recurring_item_colours[item])
                if item in recurring_item_colours else
                item
            )
            for offset_point, item in table.items()
        }
        return coloured_table

    def get_extension_offset_texts(self, garden: "GardenExtended", first_tile_step_count_map: Dict[Point2D, int], offset_point: Point2D, horizontal_bias: Optional[str] = None, vertical_bias: Optional[str] = None) -> Dict[Point2D, str]:
        reference_point, extension_offsets = garden.get_extension_offsets(first_tile_step_count_map, offset_point, horizontal_bias, vertical_bias)
        if not extension_offsets:
            return {
                point: ""
                for point in extension_offsets
            }
        return {
            point: (
                str(offset)
                if point != reference_point else
                click.style("X", fg="green")
            )
            for point, offset in extension_offsets.items()
        }

    def get_extension_difference_texts(self, garden: "GardenExtended", first_tile_step_count_map: Dict[Point2D, int], offset_point: Point2D, horizontal_bias: Optional[str] = None, vertical_bias: Optional[str] = None) -> Dict[Point2D, str]:
        reference_point, extension_offsets = garden.get_extension_differences(first_tile_step_count_map, offset_point, horizontal_bias, vertical_bias)
        if not extension_offsets:
            return {
                point: ""
                for point in extension_offsets
            }
        return {
            point: str(offset)
            for point, offset in extension_offsets.items()
        }

    def make_diff_table(self, actual: Dict[Point2D, any], generated: Dict[Point2D, any]) -> Dict[Point2D, str]:
        return {
            point: (
                click.style(str(actual_value), fg=(
                    "green"
                    if actual_value == generated_value else
                    "red"
                    if generated_value is not None else
                    "magenta"
                ))
            )
            for point, actual_value in actual.items()
            for generated_value in [generated.get(point)]
        }


@dataclass
class PlayContext:
    step_count: int
    garden_name: str
    garden: "GardenExtended"
    generator_step_count: int
    test_garden: "GardenExtended"
    input_garden: "GardenExtended"

    @classmethod
    def from_input_garden_text(cls, text: str) -> "PlayContext":
        return cls.from_input_garden(GardenExtended.from_map_text(text))

    @classmethod
    def from_input_garden(cls, input_garden: "GardenExtended") -> "PlayContext":
        test_garden = GardenExtended.from_map_text("""
        ...........
        .....###.#.
        .###.##..#.
        ..#.#...#..
        ....#.#....
        .##..S####.
        .##..#...#.
        .......##..
        .##.#.####.
        .##..##.##.
        ...........
        """)
        return cls(
            step_count=0,
            garden_name="test",
            garden=test_garden,
            generator_step_count=70,
            test_garden=test_garden,
            input_garden=input_garden,
        )

    @cached_property
    def first_tile_step_count_map(self) -> Dict[Point2D, int]:
        return self.garden.get_first_tile_step_count_map(self.step_count)

    @cached_property
    def other_tiles(self) -> Set[Point2D]:
        return self.garden.get_reachable_tiles_after_steps_with_map(self.step_count, self.first_tile_step_count_map)

    @cached_property
    def boundaries(self) -> Tuple[Point2D, Point2D]:
        return min_and_max_tuples(self.first_tile_step_count_map)

    @cached_property
    def extension_boundaries(self) -> Tuple[Point2D, Point2D]:
        (min_x, min_y), (max_x, max_y) = self.boundaries
        min_extension_x = min_x // self.garden.width
        min_extension_y = min_y // self.garden.height
        max_extension_x = (max_x + 1) // self.garden.width
        max_extension_y = (max_y + 1) // self.garden.height
        return Point2D(min_extension_x, min_extension_y), Point2D(max_extension_x, max_extension_y)

    @cached_property
    def extension_count(self) -> Point2D:
        return Point2D(
            self.extension_boundaries[1].x - self.extension_boundaries[0].x + 1,
            self.extension_boundaries[1].y - self.extension_boundaries[0].y + 1,
        )

    @property
    def offset_points(self) -> Iterable[Point2D]:
        (min_extension_x, min_extension_y), (max_extension_x, max_extension_y) = self.extension_boundaries
        return (
            Point2D(x, y)
            for x in range(min_extension_x, max_extension_x + 1)
            for y in range(min_extension_y, max_extension_y + 1)
        )

    @cached_property
    def generator(self) -> "ExtensionGenerator":
        return self.garden.get_generator(self.generator_step_count, first_tile_step_count_map=self.first_tile_step_count_map)

    def to_step_count(self, step_count: int) -> "PlayContext":
        return PlayContext(
            step_count=step_count,
            garden_name=self.garden_name,
            generator_step_count=self.generator_step_count,
            garden=self.garden,
            test_garden=self.test_garden,
            input_garden=self.input_garden,
        )

    def switch_to(self, garden_name: str) -> "PlayContext":
        return PlayContext(
            step_count=self.step_count,
            garden_name=garden_name,
            garden={"test": self.test_garden, "input": self.input_garden}[garden_name],
            generator_step_count={"test": 70, "input": 1000}[garden_name],
            test_garden=self.test_garden,
            input_garden=self.input_garden,
        )


class GardenExtended(part_a.Garden):
    def __str__(self, other_tiles: Optional[Set[Point2D]] = None, show_start: bool = False, show_extensions: bool = False, matches_and_mismatches: Optional[Tuple[Set[Point2D], Set[Point2D]]] = None) -> str:
        plots = self.plots
        if other_tiles:
            plots = plots | other_tiles
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(plots)
        if show_extensions:
            def add_extension(text: str, position: Point2D) -> str:
                if (position.x // self.width) % 2 == (position.y // self.height) % 2:
                    return text
                return click.style(text, bg="white")
        else:
            def add_extension(text: str, position: Point2D) -> str:
                return text
        if show_start:
            def add_start(text: str, position: Point2D) -> str:
                if position != self.start:
                    return text
                return click.style(text, fg="green")
        else:
            def add_start(text: str, position: Point2D) -> str:
                return text
        if matches_and_mismatches:
            matches, mismatches = matches_and_mismatches
            def add_matches_and_mismatches(text: str, position: Point2D) -> str:
                if position in matches:
                    return click.style(text, fg="green")
                elif position in mismatches:
                    return click.style(text, fg="red")
                return text
        else:
            def add_matches_and_mismatches(text: str, position: Point2D) -> str:
                return text
        output = "\n".join(
            "".join(
                add_matches_and_mismatches(add_start(add_extension((
                    "O"
                    if other_tiles and position in other_tiles else
                    "S"
                    if position == self.start else
                    "."
                    if position in self else
                    "#"
                ), position), position), position)
                for x in range(min_x, max_x + 1)
                for position in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
        )
        return output

    def show_with_other_tiles(self, other_tiles: Set[Point2D], show_start: bool = False, show_extensions: bool = False, matches_and_mismatches: Optional[Tuple[Set[Point2D], Set[Point2D]]] = None) -> str:
        return self.__str__(other_tiles=other_tiles, show_start=show_start, show_extensions=show_extensions, matches_and_mismatches=matches_and_mismatches)

    def __contains__(self, point: Point2D) -> bool:
        return Point2D(point.x % self.width, point.y % self.height) in self.plots

    @cached_property
    def size(self) -> Tuple[int, int]:
        _, (width, height) = min_and_max_tuples(self.plots)
        return width + 1, height + 1

    @cached_property
    def width(self) -> int:
        width, _ = self.size
        return width

    @cached_property
    def height(self) -> int:
        _, height = self.size
        return height

    def get_reachable_tiles_after_1_step(self, other_tiles: Optional[Set[Point2D]] = None) -> Set[Point2D]:
        if other_tiles is None:
            other_tiles = {self.start}
        new_other_tiles = set()
        for tile in other_tiles:
            for neighbour in tile.get_manhattan_neighbours():
                if neighbour not in self:
                    continue
                new_other_tiles.add(neighbour)
        return new_other_tiles

    def get_reachable_tiles_after_steps_with_map(self, step_count, first_tile_step_count_map: Dict[Point2D, int]) -> Set[Point2D]:
        self.get_first_tile_step_count_map(step_count, first_tile_step_count_map)
        return {
            tile
            for tile, first_tile_step_count in first_tile_step_count_map.items()
            if first_tile_step_count <= step_count
            and step_count % 2 == first_tile_step_count % 2
        }

    def get_reachable_tile_count_after_steps(self, steps: int, other_tiles: Optional[Set[Point2D]] = None) -> int:
        pass
        """
        >>> _garden = GardenExtended.from_map_text('''
        ...     ...........
        ...     .....###.#.
        ...     .###.##..#.
        ...     ..#.#...#..
        ...     ....#.#....
        ...     .##..S####.
        ...     .##..#...#.
        ...     .......##..
        ...     .##.#.####.
        ...     .##..##.##.
        ...     ...........
        ... ''')
        >>> _garden.get_reachable_tile_count_after_steps(6)
        16
        >>> _garden.get_reachable_tile_count_after_steps(10)
        50
        >>> _garden.get_reachable_tile_count_after_steps(50)
        1594
        >>> _garden.get_reachable_tile_count_after_steps(100)
        6536
        >>> _garden.get_reachable_tile_count_after_steps(500)
        167004
        >>> _garden.get_reachable_tile_count_after_steps(1000)
        668697
        >>> _garden.get_reachable_tile_count_after_steps(5000)
        16733044
        """
        first_tile_step_count_map = self.get_first_tile_step_count_map(steps)
        return sum(
            1
            for tile, first_tile_step_count in first_tile_step_count_map.items()
            if (first_tile_step_count <= steps)
            and ((steps % 2) == (first_tile_step_count % 2))
        )

    def get_reachable_tiles_after_steps(self, steps: int, other_tiles: Optional[Set[Point2D]] = None, first_tile_step_count_map: Optional[Dict[Point2D, int]] = None) -> Set[Point2D]:
        first_tile_step_count_map = self.get_first_tile_step_count_map(steps, first_tile_step_count_map=first_tile_step_count_map)
        return {
            tile
            for tile, first_tile_step_count in first_tile_step_count_map.items()
            if first_tile_step_count <= steps
            and steps % 2 == first_tile_step_count % 2
        }

    def get_first_tile_step_count_map(self, step_count: int, first_tile_step_count_map: Optional[Dict[Point2D, int]] = None, debugger: Debugger = Debugger(enabled=False)) -> Dict[Point2D, int]:
        if first_tile_step_count_map is None:
            first_tile_step_count_map = {self.start: 0}
        queue = []
        for index, (tile, first_tile_step_count) in debugger.stepping(enumerate(first_tile_step_count_map.items())):
            if first_tile_step_count >= step_count:
                return first_tile_step_count_map
            if first_tile_step_count < step_count:
                queue.append(tile)
            if debugger.should_report():
                debugger.default_report_if(f"Stepped through {index + 1}/{len(first_tile_step_count_map)} items, queued {len(queue)}")
        while debugger.step_if(queue):
            tile = queue.pop(0)
            for neighbour in tile.get_manhattan_neighbours():
                if neighbour in first_tile_step_count_map:
                    continue
                if neighbour not in self:
                    continue
                new_step_count = first_tile_step_count_map[tile] + 1
                first_tile_step_count_map[neighbour] = new_step_count
                if new_step_count >= step_count:
                    continue
                queue.append(neighbour)
            if debugger.should_report():
                debugger.default_report_if(f"{len(queue)} remaining, {len(first_tile_step_count_map)} total")
        return first_tile_step_count_map

    def get_generator(self, min_steps: int, first_tile_step_count_map: Optional[Dict[Point2D, int]] = None, debugger: Debugger = Debugger(enabled=False)) -> "ExtensionGenerator":
        return ExtensionGenerator.from_garden(self, min_steps, first_tile_step_count_map=first_tile_step_count_map, debugger=debugger)

    def get_extension(self, first_tile_step_count_map: Dict[Point2D, int], offset_point: Point2D, normalise_point: bool = False) -> Dict[Point2D, int]:
        offset = Point2D(offset_point.x * self.width, offset_point.y * self.height)
        return {
            (
                extension_point
                if not normalise_point else
                point
            ): first_tile_step_count_map[extension_point]
            for x in range(self.width)
            for y in range(self.height)
            for point in [Point2D(x, y)]
            for extension_point in [point.offset(offset)]
            if extension_point in first_tile_step_count_map
        }

    def get_extension_offsets(self, first_tile_step_count_map: Dict[Point2D, int], offset_point: Point2D, horizontal_bias: Optional[str] = None, vertical_bias: Optional[str] = None) -> Tuple[Point2D, Dict[Point2D, int]]:
        offset = Point2D(offset_point.x * self.width, offset_point.y * self.height)
        horizontal_bias = horizontal_bias or (
            "L"
            if offset_point.x > 0 else
            "C"
            if offset_point.x == 0 else
            "R"
        )
        vertical_bias = vertical_bias or (
            "T"
            if offset_point.y > 0 else
            "C"
            if offset_point.y == 0 else
            "B"
        )
        reference_point = Point2D(
            (
                0
                if horizontal_bias == "L" else
                self.width // 2
                if horizontal_bias == "C" else
                self.width - 1
            ),
            (
                0
                if vertical_bias == "T" else
                self.height // 2
                if vertical_bias == "C" else
                self.height - 1
            ),
        ).offset(offset)
        extension_offsets = {
            point: (
                first_tile_step_count_map[extension_point] - first_tile_step_count_map[reference_point]
            )
            for x in range(self.width)
            for y in range(self.height)
            for point in [Point2D(x, y)]
            for extension_point in [point.offset(offset)]
            if extension_point in first_tile_step_count_map
            and reference_point in first_tile_step_count_map
        }
        return reference_point.offset(offset, -1), extension_offsets

    def get_extension_differences(self, first_tile_step_count_map: Dict[Point2D, int], offset_point: Point2D, horizontal_bias: Optional[str] = None, vertical_bias: Optional[str] = None) -> Tuple[Point2D, Dict[Point2D, int]]:
        offset = Point2D(offset_point.x * self.width, offset_point.y * self.height)
        horizontal_bias = horizontal_bias or (
            "L"
            if offset_point.x > 0 else
            "C"
            if offset_point.x == 0 else
            "R"
        )
        vertical_bias = vertical_bias or (
            "T"
            if offset_point.y > 0 else
            "C"
            if offset_point.y == 0 else
            "B"
        )
        previous_offset_point = Point2D(
            (
                -1
                if horizontal_bias == "L" else
                0
                if horizontal_bias == "C" else
                1
            ),
            (
                -1
                if vertical_bias == "T" else
                0
                if vertical_bias == "C" else
                1
            ),
        )
        previous_offset = Point2D(previous_offset_point.x * self.width, previous_offset_point.y * self.height)
        extension_differences = {
            point: (
                first_tile_step_count_map[extension_point] - first_tile_step_count_map[previous_extension_point]
            )
            for x in range(self.width)
            for y in range(self.height)
            for point in [Point2D(x, y)]
            for extension_point in [point.offset(offset)]
            for previous_extension_point in [point.offset(previous_offset)]
            if extension_point in first_tile_step_count_map
            and previous_extension_point in first_tile_step_count_map
        }
        return previous_offset_point.offset(offset, -1), extension_differences

    def get_extension_reachable_tile_count(self, step_count: int, first_tile_step_count_map: Dict[Point2D, int], offset_point: Point2D) -> int:
        offset = Point2D(offset_point.x * self.width, offset_point.y * self.height)
        return sum(
            1
            for x in range(self.width)
            for y in range(self.height)
            for point in [Point2D(x, y)]
            for extension_point in [point.offset(offset)]
            if extension_point in first_tile_step_count_map
            for first_tile_step_count in [first_tile_step_count_map[extension_point]]
            if (first_tile_step_count <= step_count)
            and ((step_count % 2) == (first_tile_step_count % 2))
        )

    def get_extension_reachable_tiles(self, step_count: int, first_tile_step_count_map: Dict[Point2D, int], offset_point: Point2D) -> Set[Point2D]:
        offset = Point2D(offset_point.x * self.width, offset_point.y * self.height)
        return {
            point
            for x in range(self.width)
            for y in range(self.height)
            for point in [Point2D(x, y)]
            for extension_point in [point.offset(offset)]
            if extension_point in first_tile_step_count_map
            for first_tile_step_count in [first_tile_step_count_map[extension_point]]
            if (first_tile_step_count <= step_count)
            and ((step_count % 2) == (first_tile_step_count % 2))
        }


@dataclass
class ExtensionGenerator:
    width: int
    height: int
    center_values: Dict[Point2D, int]
    reference_points_by_direction: Dict[Direction8, Point2D]
    offsets_by_direction: Dict[Direction8, List[Dict[Point2D, int]]]

    @classmethod
    def from_garden(cls, garden: GardenExtended, step_count: int, first_tile_step_count_map: Optional[Dict[Point2D, int]] = None, debugger: Debugger = Debugger(enabled=False)) -> "ExtensionGenerator":
        first_tile_step_count_map = garden.get_first_tile_step_count_map(step_count, first_tile_step_count_map=first_tile_step_count_map, debugger=debugger)
        center_values = {
            point: first_tile_step_count_map[point]
            for x in range(garden.width)
            for y in range(garden.height)
            for point in [Point2D(x, y)]
            if point in first_tile_step_count_map
        }
        values_and_offsets_by_direction = {
            direction: cls.get_direction_extension_values_and_offsets(garden, first_tile_step_count_map, direction)
            for direction in Direction8
        }
        return cls(
            width=garden.width,
            height=garden.height,
            center_values=center_values,
            reference_points_by_direction={
                direction: reference_point
                for direction, (reference_point, _, _) in values_and_offsets_by_direction.items()
            },
            offsets_by_direction={
                direction: offsets_list
                for direction, (_, offsets_list, _) in values_and_offsets_by_direction.items()
            },
        )

    @classmethod
    def get_direction_extension_values_and_offsets(cls, garden: GardenExtended, first_tile_step_count_map: Dict[Point2D, int], direction: Direction8) -> Tuple[Point2D, List[Dict[Point2D, int]], Dict[Point2D, int]]:
        offsets_lists: List[Dict[Point2D, int]] = []
        previous_extension_offsets: Optional[Dict[Point2D, int]] = None
        reference_point: Optional[Point2D] = None
        for direction_offset in count(1):
            offset_point = direction.offset.resize(direction_offset)
            reference_point, extension_offsets = garden.get_extension_offsets(first_tile_step_count_map, offset_point)
            if extension_offsets == previous_extension_offsets:
                break
            offsets_lists.append(extension_offsets)
            previous_extension_offsets = extension_offsets
        return reference_point, offsets_lists, previous_extension_offsets

    def get_reachable_tile_count(self, step_count: int) -> int:
        """
        >>> _garden = GardenExtended.from_map_text('''
        ...     ...........
        ...     .....###.#.
        ...     .###.##..#.
        ...     ..#.#...#..
        ...     ....#.#....
        ...     .##..S####.
        ...     .##..#...#.
        ...     .......##..
        ...     .##.#.####.
        ...     .##..##.##.
        ...     ...........
        ... ''')
        >>> _generator = _garden.get_generator(70)
        >>> _generator.get_reachable_tile_count(6)
        16
        >>> _generator.get_reachable_tile_count(10)
        50
        >>> _generator.get_reachable_tile_count(50)
        1594
        >>> _generator.get_reachable_tile_count(100)
        6536
        >>> _generator.get_reachable_tile_count(500)
        167004
        >>> _generator.get_reachable_tile_count(1000)
        668697
        >>> _generator.get_reachable_tile_count(5000)
        16733044
        """
        max_x, max_y = self.get_max_size_for_steps(step_count)
        max_distance = max(max_x, max_y)
        safe_line_count = 4
        if max_distance <= safe_line_count * 2:
            return sum(
                self.get_extension_reachable_tile_count(step_count, Point2D(x, y))
                for x in range(-max_distance, max_distance + 1)
                for y in range(-max_distance, max_distance + 1)
            )
        line_count = 0
        total_count = 0
        line_increment = (
            self.get_extension_reachable_tile_count(step_count, Point2D(0, 0))
            + self.get_extension_reachable_tile_count(step_count, Point2D(1, 0))
        )
        for y in range(-max_distance, -max_distance + safe_line_count):
            line_count = self.get_extension_line_reachable_tile_count(step_count, y, max_distance)
            total_count += line_count
        range_count = len(range(-max_distance + safe_line_count, -safe_line_count))
        total_count += (
            line_count * range_count
            + line_increment * range_count * (range_count + 1) // 2
        )
        # for y in range(-max_distance + safe_line_count, -safe_line_count):
        #     line_count += line_increment
        #     actual_line_count = self.get_extension_line_reachable_tile_count(step_count, y, max_distance)
        #     if line_count != actual_line_count:
        #         raise Exception(f"Actual {actual_line_count} != generated {line_count}, y={y}, line_increment={line_increment}")
        #     total_count += line_count
        for y in range(-safe_line_count, safe_line_count + 1):
            line_count = self.get_extension_line_reachable_tile_count(step_count, y, max_distance)
            total_count += line_count
        range_count = len(range(safe_line_count + 1, max_distance - safe_line_count))
        total_count += (
            line_count * range_count
            - line_increment * range_count * (range_count + 1) // 2
        )
        # for y in range(safe_line_count + 1, max_distance - safe_line_count):
        #     line_count -= line_increment
        #     actual_line_count = self.get_extension_line_reachable_tile_count(step_count, y, max_distance)
        #     if line_count != actual_line_count:
        #         raise Exception(f"Actual {actual_line_count} != generated {line_count}, y={y}, line_increment={line_increment}")
        #     total_count += line_count
        for y in range(max_distance - safe_line_count, max_distance + 1):
            line_count = self.get_extension_line_reachable_tile_count(step_count, y, max_distance)
            total_count += line_count
        return total_count

    def get_max_size_for_steps(self, step_count: int) -> Point2D:
        return Point2D(
            self.get_max_distance_for_steps(step_count, Direction8.Right),
            self.get_max_distance_for_steps(step_count, Direction8.Down),
        )

    def get_max_distance_for_steps(self, step_count: int, offset_direction: Direction8) -> int:
        offset_point = Point2D(0, 0)
        extension = self.center_values
        unit_offset_point = offset_direction.offset
        offsets_list = self.offsets_by_direction[offset_direction]
        offset_count = 0
        while max(extension.values()) < step_count and offset_count < len(offsets_list):
            offset_point = offset_point.offset(unit_offset_point)
            extension = self.add_to_extension(self.center_values, offset_point)
            offset_count += 1
        if max(extension.values()) >= step_count:
            return offset_count + 1
        reference_point = self.reference_points_by_direction[offset_direction]
        previous_offset = unit_offset_point.resize(-1)
        reference_increment = abs(unit_offset_point.x) + abs(unit_offset_point.y)
        previous_point = Point2D(
            (reference_point.x + previous_offset.x) % self.width,
            (reference_point.y + previous_offset.y) % self.height,
        )
        offsets = offsets_list[-1]
        rest_count = (step_count - extension[previous_point] + offsets[previous_point]) // (offsets[previous_point] + reference_increment) + 1
        rest_count = max(rest_count, 0)
        # total_reference_value = extension[previous_point] + offsets[previous_point] * (rest_count - 1) + reference_increment * rest_count
        return len(offsets_list) + rest_count + 1

    def get_extension_reachable_tiles(self, step_count: int, offset_point: Point2D) -> Set[Point2D]:
        offset = Point2D(offset_point.x * self.width, offset_point.y * self.height)
        extension = self.get_extension(offset_point)
        return {
            point
            for x in range(self.width)
            for y in range(self.height)
            for point in [Point2D(x, y)]
            for extension_point in [point.offset(offset)]
            if extension_point in extension
            for first_tile_step_count in [extension[extension_point]]
            if (first_tile_step_count <= step_count)
            and ((step_count % 2) == (first_tile_step_count % 2))
        }

    def get_extension_line_reachable_tile_count(self, step_count: int, y: int, max_distance: int) -> int:
        max_x = max_distance - abs(y)
        safe_tile_count = 4
        if max_x <= safe_tile_count * 2 + 1:
            ranges = [
                range(-max_x, max_x + 1)
            ]
            rest_range = range(1, 0)
            even_tile_increment, odd_tile_increment = 0, 0
        else:
            ranges = [
                range(-max_x, -max_x + safe_tile_count),
                range(max_x + 1 - safe_tile_count, max_x + 1),
            ]
            rest_range = range(-max_x + safe_tile_count, max_x + 1 - safe_tile_count)
            even_tile_increment, odd_tile_increment = (
                self.get_extension_reachable_tile_count(step_count, Point2D(0, y)),
                self.get_extension_reachable_tile_count(step_count, Point2D(1, y))
            )
        line_count = sum(
            self.get_extension_reachable_tile_count(step_count, Point2D(x, y))
            for _range in ranges
            for x in _range
        )
        if len(rest_range):
            if rest_range.start % 2 == 0 and (rest_range.stop - 1) % 2 == 0:
                assert len(rest_range) % 2 == 1, f"Range {rest_range} length {len(rest_range)} was not odd"
                tiles_count = (
                    even_tile_increment * (len(rest_range) + 1) // 2
                    + odd_tile_increment * (len(rest_range) - 1) // 2
                )
                line_count += tiles_count
            elif rest_range.start % 2 == 1 and (rest_range.stop - 1) % 2 == 1:
                assert len(rest_range) % 2 == 1, f"Range {rest_range} length {len(rest_range)} was not odd"
                tiles_count = (
                    even_tile_increment * (len(rest_range) - 1) // 2
                    + odd_tile_increment * (len(rest_range) + 1) // 2
                )
                line_count += tiles_count
            else:
                assert len(rest_range) % 2 == 0, f"Range {rest_range} length {len(rest_range)} was not even"
                tiles_count = (
                    even_tile_increment * len(rest_range) // 2
                    + odd_tile_increment * len(rest_range) // 2
                )
                line_count += tiles_count
            # actual_tiles_count = 0
            # for x in rest_range:
            #     actual_tiles_count += (
            #         even_tile_increment
            #         if x % 2 == 0 else
            #         odd_tile_increment
            #     )
            # if actual_tiles_count != tiles_count:
            #     raise Exception(f"Actual tiles count {actual_tiles_count} != generated tiles count {tiles_count}, range={rest_range}, y={y}, max_x={max_x}, even={even_tile_increment}, odd={odd_tile_increment}")
        # for x in rest_range:
        #     tile_count = (
        #         even_tile_increment
        #         if x % 2 == 0 else
        #         odd_tile_increment
        #     )
        #     # actual_tile_count = self.get_extension_reachable_tile_count(step_count, Point2D(x, y))
        #     # if actual_tile_count != tile_count:
        #     #     raise Exception(f"Actual tile count {actual_tile_count} != generated tile count {tile_count}, x={x}, y={y}, max_x={max_x}")
        #     line_count += tile_count
        return line_count

    def get_extension_reachable_tile_count(self, step_count: int, offset_point: Point2D) -> int:
        offset = Point2D(offset_point.x * self.width, offset_point.y * self.height)
        extension = self.get_extension(offset_point)
        return sum(
            1
            for x in range(self.width)
            for y in range(self.height)
            for point in [Point2D(x, y)]
            for extension_point in [point.offset(offset)]
            if extension_point in extension
            for first_tile_step_count in [extension[extension_point]]
            if (first_tile_step_count <= step_count)
            and ((step_count % 2) == (first_tile_step_count % 2))
        )

    def get_extension(self, offset_point: Point2D) -> Dict[Point2D, int]:
        extension = self.center_values
        if offset_point.y == 0 or offset_point.x == 0 or abs(offset_point.x) == abs(offset_point.y):
            extension = self.add_to_extension(extension, offset_point)
        else:
            iteration_count = min(abs(offset_point.x), abs(offset_point.y))
            diagonal_offset_point = offset_point.to_unit().resize(iteration_count)
            extension = self.add_to_extension(extension, diagonal_offset_point)
            rest_offset_point = offset_point.offset(diagonal_offset_point, factor=-1)
            offset_direction = Direction8.from_offset(diagonal_offset_point.to_unit())
            extension = self.add_to_extension(extension, rest_offset_point, offset_direction=offset_direction)
        offset = Point2D(offset_point.x * self.width, offset_point.y * self.height)
        return {
            point.offset(offset): value
            for point, value in extension.items()
        }
        return extension

    def add_to_extension(self, extension: Dict[Point2D, int], offset_point: Point2D, offset_direction: Optional[Direction8] = None) -> Dict[Point2D, int]:
        if offset_point == Point2D(0, 0):
            return extension
        unit_offset_point = offset_point.to_unit()
        if offset_direction is None:
            offset_direction = Direction8.from_offset(unit_offset_point)
        offsets_list = self.offsets_by_direction[offset_direction]
        reference_point = self.reference_points_by_direction[offset_direction]
        previous_offset = unit_offset_point.resize(-1)
        reference_increment = abs(unit_offset_point.x) + abs(unit_offset_point.y)
        iteration_count = max(abs(offset_point.x), abs(offset_point.y))
        previous_point = Point2D(
            (reference_point.x + previous_offset.x) % self.width,
            (reference_point.y + previous_offset.y) % self.height,
        )
        for index in range(min(iteration_count, len(offsets_list) - 1)):
            offsets = offsets_list[min(index, len(offsets_list) - 1)]
            reference_value = extension[previous_point] + reference_increment
            extension = self.increment_extension(offsets, reference_value)
        if iteration_count >= len(offsets_list):
            rest_count = iteration_count - len(offsets_list) + 1
            offsets = offsets_list[-1]
            total_reference_value = extension[previous_point] + offsets[previous_point] * (rest_count - 1) + reference_increment * rest_count
            extension = self.increment_extension(offsets, total_reference_value)
        return extension

    def offset_extension(self, extension: Dict[Point2D, int], offsets: Dict[Point2D, int], factor: int = 1) -> Dict[Point2D, int]:
        return {
            point: value + offsets[point] * factor
            for point, value in extension.items()
        }

    def increment_extension(self, extension: Dict[Point2D, int], increment: int) -> Dict[Point2D, int]:
        return {
            point: value + increment
            for point, value in extension.items()
        }


Challenge.main()
challenge = Challenge()
