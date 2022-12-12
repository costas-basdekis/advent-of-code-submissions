#!/usr/bin/env python3
from dataclasses import dataclass
from string import ascii_lowercase
from typing import ClassVar, Dict, Optional, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Cls, Self


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        447
        """
        return DistanceMap\
            .from_map_text(_input)\
            .fill_map()\
            .get_min_steps_required()


@dataclass
class DistanceMap:
    distances: [[int]]
    elevation_map: "ElevationMap"

    print_map: ClassVar[Dict[int, str]] = {
        -1: "*",
        **{
            distance: str(distance)
            for distance in range(10)
        },
        **dict(enumerate(ascii_lowercase, 10)),
    }

    @classmethod
    def from_map_text(
        cls: Cls["DistanceMap"], map_text: str,
    ) -> Self["DistanceMap"]:
        """
        >>> print(DistanceMap.from_map_text(
        ...     "Sabqponm\\n"
        ...     "abcryxxl\\n"
        ...     "accszExk\\n"
        ...     "acctuvwj\\n"
        ...     "abdefghi"
        ... ))
        ********
        ********
        ********
        ********
        ********
        """
        return cls.from_elevation_map(ElevationMap.from_map_text(map_text))

    @classmethod
    def from_elevation_map(
        cls: Cls["DistanceMap"], elevation_map: "ElevationMap",
    ) -> Self["DistanceMap"]:
        return cls(
            distances=cls.get_initial_distances(elevation_map),
            elevation_map=elevation_map,
        )

    @classmethod
    def get_initial_distances(cls, elevation_map: "ElevationMap") -> [[int]]:
        return [
            [-1] * len(elevation_map.heights[0])
            for _ in range(len(elevation_map.heights))
        ]

    def get_min_steps_required(self) -> int:
        """
        >>> DistanceMap.from_map_text(
        ...     "Sabqponm\\n"
        ...     "abcryxxl\\n"
        ...     "accszExk\\n"
        ...     "acctuvwj\\n"
        ...     "abdefghi"
        ... ).fill_map().get_min_steps_required()
        31
        """
        steps = self[self.elevation_map.target]
        if steps == -1:
            raise Exception(f"Target is unreachable")
        return steps

    def fill_map(self: Self["DistanceMap"]) -> Self["DistanceMap"]:
        """
        >>> print(DistanceMap.from_map_text(
        ...     "Sabqponm\\n"
        ...     "abcryxxl\\n"
        ...     "accszExk\\n"
        ...     "acctuvwj\\n"
        ...     "abdefghi"
        ... ).fill_map())
        012jihgf
        123ktsre
        234luvqd
        345mnopc
        456789ab
        """
        self.distances = \
            self.get_initial_distances(elevation_map=self.elevation_map)
        start = self.get_fill_start()
        queue = [start]
        self[start] = 0
        while queue:
            item = queue.pop(0)
            next_neighbours = [
                neighbour
                for neighbour in item.get_manhattan_neighbours()
                if self.is_neighbour_valid(item, neighbour)
            ]
            distance = self[item]
            for neighbour in next_neighbours:
                self[neighbour] = distance + 1
            queue.extend(next_neighbours)
            if self.should_stop_filling():
                break
        return self

    def get_fill_start(self):
        start = self.elevation_map.start
        return start

    def should_stop_filling(self) -> bool:
        return self[self.elevation_map.target] > -1

    def is_neighbour_valid(self, current: Point2D, neighbour: Point2D) -> bool:
        neighbour_distance = self.get(neighbour)
        if neighbour_distance is None:
            return False
        if neighbour_distance != -1:
            return False
        if not self.can_move_to_neighbour(current, neighbour):
            return False
        return True

    def can_move_to_neighbour(
        self, current: Point2D, neighbour: Point2D,
    ) -> bool:
        return (
            self.elevation_map[neighbour] <= (self.elevation_map[current] + 1)
        )

    def __str__(self) -> "str":
        return "\n".join(
            "".join(
                self.print_map[distance]
                for distance in line
            )
            for line in self.distances
        )

    def __getitem__(self, item: Point2D) -> int:
        if item.x < 0 or item.y < 0:
            raise KeyError(item)
        try:
            return self.distances[item.y][item.x]
        except IndexError:
            raise KeyError(item)

    def __setitem__(self, key: Point2D, value: int) -> None:
        if key.x < 0 or key.y < 0:
            raise KeyError(key)
        try:
            self.distances[key.y][key.x] = value
        except IndexError:
            raise KeyError(key)

    def get(self, key: Point2D, default: Optional[int] = None) -> Optional[int]:
        try:
            return self[key]
        except KeyError:
            return default


@dataclass
class ElevationMap:
    heights: [[int]]
    start: Point2D
    target: Point2D

    parse_map: ClassVar[Dict[str, int]] = {
        "S": 1,
        "E": 26,
        **{
            letter: height
            for height, letter in enumerate(ascii_lowercase, 1)
        },
    }
    print_map: ClassVar[Dict[int, str]] = dict(enumerate(ascii_lowercase, 1))

    @classmethod
    def from_map_text(cls, map_text: str) -> "ElevationMap":
        """
        >>> print(ElevationMap.from_map_text(
        ...     "Sabqponm\\n"
        ...     "abcryxxl\\n"
        ...     "accszExk\\n"
        ...     "acctuvwj\\n"
        ...     "abdefghi"
        ... ))
        Sabqponm
        abcryxxl
        accszExk
        acctuvwj
        abdefghi
        """
        lines = map_text.strip().splitlines()
        return cls(
            heights=[
                [
                    cls.parse_map[character]
                    for character in line
                ]
                for line in lines
            ],
            start=cls.get_position_in_lines(lines, "S"),
            target=cls.get_position_in_lines(lines, "E"),
        )

    @classmethod
    def get_position_in_lines(cls, lines: [str], needle: str) -> Point2D:
        line, = [
            _line
            for _line in lines
            if needle in _line
        ]
        return Point2D(list(line).index(needle), lines.index(line))

    def __str__(self) -> str:
        return "\n".join(
            "".join(
                "S"
                if point == self.start else
                "E"
                if point == self.target else
                self.print_map[height]
                for x, height in enumerate(line)
                for point in [Point2D(x, y)]
            )
            for y, line in enumerate(self.heights)
        )

    def __getitem__(self, item: Point2D) -> int:
        return self.heights[item.y][item.x]

    def __setitem__(self, key: Point2D, value: int) -> None:
        self.heights[key.y][key.x] = value


Challenge.main()
challenge = Challenge()
