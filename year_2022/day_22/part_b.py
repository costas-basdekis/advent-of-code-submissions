#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import ClassVar, Dict, List, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples
from year_2022.day_22 import part_a
from year_2022.day_22.part_a import Direction


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> solution = Challenge().default_solve()
        >>> 130280 < solution
        True
        >>> solution
        42
        """
        return PathFinderExtended\
            .from_map_text(_input)\
            .get_password()

    def play(self):
        path_finder = PathFinderExtended\
            .from_map_text(self.input)\
            .trace_traverse()
        path_finder.play()


class PathFinderExtended(part_a.PathFinder["BoardExtended"]):
    """
    >>> path_finder = PathFinderExtended.from_map_text(Challenge().input).trace_traverse()
    >>> path_finder.board.calculate_next_point(Point2D(0, 159), Direction.Right)
    (Point2D(x=1, y=159), Direction.Right)
    >>> list(path_finder.instructions[2].iterate_advance(path_finder.board, Point2D(59, 0), Direction.Up))
    [(Point2D(x=0, y=159), Direction.Right),
        (Point2D(x=1, y=159), Direction.Right),
        (Point2D(x=2, y=159), Direction.Right)]
    >>> path_finder.path[10:14]
    [(Point2D(x=59, y=0), Direction.Up, 'L'),
        (Point2D(x=0, y=159), Direction.Right, '3'),
        (Point2D(x=1, y=159), Direction.Right, '3'),
        (Point2D(x=2, y=159), Direction.Right, '3')]
    """


@dataclass
class BoardExtended(part_a.Board):
    continuation_map: "ContinuationMap" = field(default_factory=lambda: ContinuationMap.from_preset())

    def get_next_point_wrapped(self, point: Point2D, direction: Direction) -> Tuple[Point2D, Direction]:
        """
        >>> board = BoardExtended.from_board_text(Challenge().input.strip("\\n").split("\\n\\n")[0])
        >>> board.calculate_next_point(Point2D(0, 159), Direction.Right)
        (Point2D(x=1, y=159), Direction.Right)
        """
        new_pair =  self.continuation_map[(point, direction)]
        return new_pair


Region = str
Position = Point2D
Range = Tuple[Position, Position]


@dataclass
class ContinuationMap:
    continuations: Dict[Tuple[Position, Direction], Tuple[Position, Direction]]
    regions_positions: Dict[Region, Position] = field(repr=False)
    directions_boundaries: Dict[Direction, Range] = field(repr=False)
    regions_boundaries: Dict[Region, Dict[Direction, Range]] = field(repr=False)
    continuations_mappings: List[Tuple[Range, Direction, Range, Direction]] = field(repr=False)

    @classmethod
    def from_preset(cls, size: int = 50) -> "ContinuationMap":
        """
        >>> cmap = ContinuationMap.from_preset(3)
        >>> print(cmap)
           +^^^^+
           <    >
           <  vv+
           < >
           < >
           < >
        +^^  >
        <    >
        <  vv+
        < >
        < >
        +v+
        >>> cmap.regions_boundaries["D"][Direction.Up]
        (Point2D(x=0, y=6), Point2D(x=2, y=6))
        >>> cmap.regions_boundaries["C"][Direction.Left]
        (Point2D(x=3, y=3), Point2D(x=3, y=5))
        >>> ((Point2D(x=0, y=6), Point2D(x=2, y=6)), Direction.Up,
        ...     (Point2D(x=3, y=3), Point2D(x=3, y=5)), Direction.Right) in cmap.continuations_mappings
        True
        >>> cmap[(Point2D(0, 6), Direction.Up)]
        (Point2D(x=3, y=3), Direction.Right)
        >>> cmap = ContinuationMap.from_preset()
        >>> cmap[(Point2D(0, 100), Direction.Up)]
        (Point2D(x=50, y=50), Direction.Right)
        """
        regions_map = " AB\n C \nDE \nF  "
        """
         AB
         C
        DE
        F
        """

        continuations_shorthands: List[Tuple[Region, Direction, bool, Region, Direction]] = [
            ("A", Direction.Left , True , "D", Direction.Right),
            ("A", Direction.Up   , False, "F", Direction.Right),
            ("B", Direction.Up   , False, "F", Direction.Up   ),
            ("B", Direction.Right, True , "E", Direction.Left ),
            ("B", Direction.Down , False, "C", Direction.Left ),
            ("C", Direction.Left , False, "D", Direction.Down ),
            ("C", Direction.Right, False, "B", Direction.Up   ),
            ("D", Direction.Left , True , "A", Direction.Right),
            ("D", Direction.Up   , False, "C", Direction.Right),
            ("E", Direction.Right, True , "B", Direction.Left ),
            ("E", Direction.Down , False, "F", Direction.Left ),
            ("F", Direction.Left , False, "A", Direction.Down ),
            ("F", Direction.Right, False, "E", Direction.Up   ),
            ("F", Direction.Down , False, "B", Direction.Down ),
        ]
        """
         AB
         C
        DE
        F
        
        A,L: - D,R
        A,U:  !F,R
        B,U:   F,U
        B,R: - E,L
        B,D:  !C,L
        C,L:  !D,D
        C,R:  !B,U
        D,L: - A,R
        D,U:  !C,R
        E,R: - B,L
        E,D:  !F,L
        F,L:  !A,D
        F,R:  !E,U
        F,D:   B,D
        
        """

        return cls.from_regions_map(regions_map, continuations_shorthands, size)

    @classmethod
    def from_regions_map(cls, regions_map: str, continuations_shorthands: List[Tuple[Region, Direction, bool, Region, Direction]], size: int) -> "ContinuationMap":
        """
        >>> cmap = ContinuationMap.from_regions_map("A", [("A", Direction.Up, False, "A", Direction.Up)], 3)
        >>> cmap
        ContinuationMap(continuations={(Point2D(x=0, y=0), Direction.Up): (Point2D(x=0, y=2), Direction.Up),
            (Point2D(x=1, y=0), Direction.Up): (Point2D(x=1, y=2), Direction.Up),
            (Point2D(x=2, y=0), Direction.Up): (Point2D(x=2, y=2), Direction.Up)})
        >>> print(cmap)
        ^^^
        >>> cmap = ContinuationMap.from_regions_map(" A", [("A", Direction.Up, False, "A", Direction.Up)], 3)
        >>> cmap
        ContinuationMap(continuations={(Point2D(x=3, y=0), Direction.Up): (Point2D(x=3, y=2), Direction.Up),
            (Point2D(x=4, y=0), Direction.Up): (Point2D(x=4, y=2), Direction.Up),
            (Point2D(x=5, y=0), Direction.Up): (Point2D(x=5, y=2), Direction.Up)})
        >>> print(cmap)
           ^^^
        """
        regions_positions: Dict[Region, Position] = {
            region: Point2D(x, y)
            for y, line in enumerate(filter(None, map(str.rstrip, regions_map.splitlines())))
            for x, region in enumerate(line)
            if region != " "
        }

        size_minus_1 = size - 1
        directions_boundaries: Dict[Direction, Range] = {
            Direction.Up: (Point2D(0, 0), Point2D(size_minus_1, 0)),
            Direction.Down: (Point2D(0, size_minus_1), Point2D(size_minus_1, size_minus_1)),
            Direction.Left: (Point2D(0, 0), Point2D(0, size_minus_1)),
            Direction.Right: (Point2D(size_minus_1, 0), Point2D(size_minus_1, size_minus_1)),
        }

        regions_boundaries: Dict[Region, Dict[Direction, Range]] = {
            region: {
                direction: (
                    Point2D(position.x * size + direction_start_x, position.y * size + direction_start_y),
                    Point2D(position.x * size + direction_end_x, position.y * size + direction_end_y),
                )
                for direction, ((direction_start_x, direction_start_y), (direction_end_x, direction_end_y))
                in directions_boundaries.items()
            }
            for region, position in regions_positions.items()
        }

        continuations_mappings: List[Tuple[Range, Direction, Range, Direction]] = [
            (
                regions_boundaries[area_from][direction_from], direction_from,
                cls.invert_range_if(invert, regions_boundaries[area_to][direction_to.opposite]), direction_to,
            )
            for area_from, direction_from, invert, area_to, direction_to
            in continuations_shorthands
        ]

        continuations: Dict[Tuple[Position, Direction], Tuple[Position, Direction]] = {
            (position_from, direction_from): (cls.interpolate_to_range(position_from, range_from, range_to), direction_to)
            for range_from, direction_from, range_to, direction_to
            in continuations_mappings
            for ((start_x_from, start_y_from), (end_x_from, end_y_from)) in [range_from]
            for x in (range(start_x_from, end_x_from + 1) if start_x_from < end_x_from else range(end_x_from, start_x_from + 1))
            for y in (range(start_y_from, end_y_from + 1) if start_y_from < end_y_from else range(end_y_from, start_y_from + 1))
            for position_from in [Point2D(x, y)]
        }

        return cls(
            continuations,
            regions_positions,
            directions_boundaries,
            regions_boundaries,
            continuations_mappings,
        )

    @classmethod
    def invert_range(cls, _range: Range) -> Range:
        start, end = _range
        return end, start

    @classmethod
    def invert_range_if(cls, invert: bool, _range: Range) -> Range:
        if invert:
            return cls.invert_range(_range)
        return _range

    @classmethod
    def interpolate_to_range(cls, position: Position, range_from: Range, range_to: Range) -> Position:
        """
        >>> ContinuationMap.interpolate_to_range(Point2D(0, 6),
        ...     (Point2D(x=0, y=6), Point2D(x=2, y=6)), (Point2D(x=3, y=3), Point2D(x=5, y=3)))
        Point2D(x=3, y=3)
        >>> ContinuationMap.interpolate_to_range(Point2D(0, 6),
        ...     (Point2D(x=0, y=6), Point2D(x=2, y=6)), (Point2D(x=3, y=3), Point2D(x=3, y=5)))
        Point2D(x=3, y=3)
        >>> ContinuationMap.interpolate_to_range(Point2D(0, 100),
        ...     (Point2D(x=0, y=100), Point2D(x=49, y=100)), (Point2D(x=50, y=50), Point2D(x=50, y=99)))
        Point2D(x=50, y=50)
        >>> cmap = ContinuationMap.from_preset()
        >>> ContinuationMap.interpolate_to_range(Point2D(0, 100),
        ...     cmap.regions_boundaries["D"][Direction.Up], cmap.regions_boundaries["C"][Direction.Left])
        Point2D(x=50, y=50)
        """
        start_from, end_from = range_from
        distance_from = end_from.difference(start_from)
        start_to, end_to = range_to
        distance_to = end_to.difference(start_to)
        if (distance_from.x == 0) != (distance_to.x == 0):
            position = position.flip()
            start_from = start_from.flip()
            end_from = end_from.flip()
            distance_from = end_from.difference(start_from)
        assert abs(distance_from.x) == abs(distance_to.x), f"{distance_from} != {distance_to} for from={range_from} to={range_to}"
        assert abs(distance_from.y) == abs(distance_to.y)
        ratio = Point2D(
            distance_to.x // distance_from.x if distance_from.x != 0 else 0,
            distance_to.y // distance_from.y if distance_from.y != 0 else 0,
        )
        return Point2D(
            (position.x - start_from.x) * ratio.x + start_to.x,
            (position.y - start_from.y) * ratio.y + start_to.y,
        )

    def __getitem__(self, item: Tuple[Position, Direction]) -> Tuple[Position, Direction]:
        return self.continuations[item]

    DIRECTIONS_STR_MAP: ClassVar[Dict[Direction, str]] = {
        Direction.Left: "<",
        Direction.Right: ">",
        Direction.Up: "^",
        Direction.Down: "v",
    }

    def __str__(self) -> str:
        directions_by_point: Dict[Point2D, Set[Direction]] = {}
        for point, direction in self.continuations:
            directions_by_point.setdefault(point, set()).add(direction)
        _, (max_x, max_y) = min_and_max_tuples(directions_by_point)
        return "\n".join(
            "".join(
                " "
                if not directions else
                "+"
                if len(directions) > 1 else
                self.DIRECTIONS_STR_MAP[first_direction]
                for x in range(0, max_x + 1)
                for point in [Point2D(x, y)]
                for directions in [directions_by_point.get(point)]
                for first_direction in [list(directions or {None})[0]]
            )
            for y in range(0, max_y + 1)
        )
