#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Optional, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        3841
        """
        return Garden.from_map_text(_input).get_reachable_tile_count_after_steps(64)


@dataclass
class Garden:
    plots: Set[Point2D]
    start: Point2D

    @classmethod
    def from_map_text(cls, text: str) -> "Garden":
        """
        >>> print("!" + str(Garden.from_map_text('''
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
        ... ''')))
        !...........
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
        """
        plots = set()
        start = None
        for y, line in enumerate(text.strip().splitlines()):
            for x, char in enumerate(line.strip()):
                position = Point2D(x, y)
                if char == ".":
                    plots.add(position)
                elif char == "S":
                    plots.add(position)
                    start = position
        return cls(plots=plots, start=start)

    def __str__(self, other_tiles: Optional[Set[Point2D]] = None) -> str:
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.plots)
        return "\n".join(
            "".join(
                "O"
                if other_tiles and position in other_tiles else
                "S"
                if position == self.start else
                "."
                if position in self.plots else
                "#"
                for x in range(min_x, max_x + 1)
                for position in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
        )

    def show_with_other_tiles(self, other_tiles: Set[Point2D]) -> str:
        return self.__str__(other_tiles=other_tiles)

    def get_reachable_tile_count_after_steps(self, steps: int, other_tiles: Optional[Set[Point2D]] = None) -> int:
        """
        >>> _garden = Garden.from_map_text('''
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
        """
        return len(self.get_reachable_tiles_after_steps(steps, other_tiles))

    def get_reachable_tiles_after_steps(self, steps: int, other_tiles: Optional[Set[Point2D]] = None) -> Set[Point2D]:
        """
        >>> _garden = Garden.from_map_text('''
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
        >>> _other_tiles = _garden.get_reachable_tiles_after_steps(6)
        >>> print("!" + _garden.show_with_other_tiles(_other_tiles))
        !...........
        .....###.#.
        .###.##.O#.
        .O#O#O.O#..
        O.O.#.#.O..
        .##O.O####.
        .##.O#O..#.
        .O.O.O.##..
        .##.#.####.
        .##O.##.##.
        ...........
        """
        if other_tiles is None:
            other_tiles = {self.start}
        for _ in range(steps):
            other_tiles = self.get_reachable_tiles_after_1_step(other_tiles)
        return other_tiles

    def get_reachable_tiles_after_1_step(self, other_tiles: Optional[Set[Point2D]] = None) -> Set[Point2D]:
        """
        >>> _garden = Garden.from_map_text('''
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
        >>> _other_tiles = _garden.get_reachable_tiles_after_1_step()
        >>> print("!" + _garden.show_with_other_tiles(_other_tiles))
        !...........
        .....###.#.
        .###.##..#.
        ..#.#...#..
        ....#O#....
        .##.OS####.
        .##..#...#.
        .......##..
        .##.#.####.
        .##..##.##.
        ...........
        """
        if other_tiles is None:
            other_tiles = {self.start}
        new_other_tiles = set()
        for tile in other_tiles:
            new_other_tiles |= set(tile.get_manhattan_neighbours()) & self.plots
        return new_other_tiles


Challenge.main()
challenge = Challenge()
