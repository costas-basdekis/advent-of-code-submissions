#!/usr/bin/env python3
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union, Iterable, ClassVar

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples
from year_2023.day_10.part_a import Field, PipeType, Direction


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        401
        """
        return FieldExtended.from_field_text(_input).get_bound_point_count()

    def play(self):
        field = FieldExtended.from_field_text(self.input)
        loop = Loop.from_field(field)
        inside_points = loop.get_bound_points()
        print(loop.__repr__(
            only_empty_points=inside_points,
            invert_empty_points=True,
            hide_pipes=False,
            box_drawing=True,
            include_initial_empty_space=True,
        ))


class FieldExtended(Field):
    def __getitem__(self, item: Point2D) -> PipeType:
        return self.tiles[item]

    def __contains__(self, item: Point2D) -> bool:
        return item in self.tiles

    def get_bound_point_count(self) -> int:
        """
        >>> FieldExtended.from_field_text('''
        ...     ...........
        ...     .S-------7.
        ...     .|F-----7|.
        ...     .||.....||.
        ...     .||.....||.
        ...     .|L-7.F-J|.
        ...     .|..|.|..|.
        ...     .L--J.L--J.
        ...     ...........
        ... ''').get_bound_point_count()
        4
        >>> FieldExtended.from_field_text('''
        ...     ..........
        ...     .S------7.
        ...     .|F----7|.
        ...     .||....||.
        ...     .||....||.
        ...     .|L-7F-J|.
        ...     .|..||..|.
        ...     .L--JL--J.
        ...     ..........
        ... ''').get_bound_point_count()
        4
        >>> FieldExtended.from_field_text('''
        ...     .F----7F7F7F7F-7....
        ...     .|F--7||||||||FJ....
        ...     .||.FJ||||||||L7....
        ...     FJL7L7LJLJ||LJ.L-7..
        ...     L--J.L7...LJS7F-7L7.
        ...     ....F-J..F7FJ|L7L7L7
        ...     ....L7.F7||L7|.L7L7|
        ...     .....|FJLJ|FJ|F7|.LJ
        ...     ....FJL-7.||.||||...
        ...     ....L---J.LJ.LJLJ...
        ... ''').get_bound_point_count()
        8
        >>> FieldExtended.from_field_text('''
        ...     FF7FSF7F7F7F7F7F---7
        ...     L|LJ||||||||||||F--J
        ...     FL-7LJLJ||||||LJL-77
        ...     F--JF--7||LJLJ7F7FJ-
        ...     L---JF-JLJ.||-FJLJJ7
        ...     |F|F-JF---7F7-L7L|7|
        ...     |FFJF7L7F-JF7|JL---7
        ...     7-L-JL7||F7|L7F-7F7|
        ...     L.L7LFJ|||||FJL7||LJ
        ...     L7JLJL-JLJLJL--JLJ.L
        ... ''').get_bound_point_count()
        10
        """
        return len(Loop.from_field(self).get_bound_points())

    def infer_starting_position_shape(self) -> PipeType:
        """
        >>> FieldExtended.from_field_text('''
        ...     .....
        ...     .S-7.
        ...     .|.|.
        ...     .L-J.
        ...     .....
        ... ''').infer_starting_position_shape()
        PipeType.SE
        """
        connecting_neighbours = [
            neighbour
            for neighbour in self.starting_position.get_manhattan_neighbours()
            if neighbour in self.tiles
            and self.starting_position
            in self[neighbour].get_neighbours(neighbour)
        ]
        direction_by_offset = {
            direction.offset: direction
            for direction in Direction
        }
        outgoing_directions = tuple(sorted((
            # We are getting the direction from starting position towards the
            # neighbour
            direction_by_offset[neighbour.difference(self.starting_position)]
            for neighbour in connecting_neighbours
        ), key=lambda direction: direction.name))
        types_by_sorted_directions = {
            tuple(sorted(
                pipe_type.directions,
                key=lambda direction: direction.name,
            )): pipe_type
            for pipe_type in PipeType
        }
        if outgoing_directions not in types_by_sorted_directions:
            raise Exception(
                f"Could not find pipe type for outgoing directions "
                f"{outgoing_directions}")
        return types_by_sorted_directions[outgoing_directions]

    def get_loop(
        self, starting_position: Optional[Point2D] = None,
    ) -> "Loop":
        return Loop.from_field(self, starting_position)


OppositeDirections: Dict[Direction, Direction] = {
    Direction.North: Direction.South,
    Direction.South: Direction.North,
    Direction.West: Direction.East,
    Direction.East: Direction.West,
}


@dataclass
class Loop:
    tiles: Dict[Point2D, PipeType]
    bounds: Tuple[Point2D, Point2D]

    @classmethod
    def from_field(
        cls, field: FieldExtended, starting_position: Optional[Point2D] = None,
    ) -> "Loop":
        if starting_position is None:
            starting_position = field.starting_position

        seen: Set[Point2D] = {starting_position}
        stack: List[Point2D] = [starting_position]
        while stack:
            position = stack.pop(0)
            for neighbour in field.get_neighbours(position):
                if neighbour in seen:
                    continue
                seen.add(neighbour)
                stack.append(neighbour)

        tiles = {
            position: (
                field[position]
                if position in field else
                field.infer_starting_position_shape()
            )
            for position in seen
        }
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(tiles)
        return cls(tiles, (Point2D(min_x, min_y), Point2D(max_x, max_y)))

    box_drawing_map: ClassVar[Dict[PipeType, str]] = {
        PipeType.NS: "┃",
        PipeType.WE: "━",
        PipeType.SE: "┏",
        PipeType.SW: "┓",
        PipeType.NE: "┗",
        PipeType.NW: "┛",
    }

    def __repr__(
        self, only_empty_points: Optional[Iterable[Point2D]] = None,
        invert_empty_points: bool = False, hide_pipes: bool = False,
        box_drawing: bool = False, include_initial_empty_space: bool = False,
    ) -> str:
        """
        >>> print(FieldExtended.from_field_text('''
        ...     .....
        ...     .S-7.
        ...     .|.|.
        ...     .L-J.
        ...     .....
        ... ''').get_loop())
        F-7
        |.|
        L-J
        >>> print(FieldExtended.from_field_text('''
        ...     ..........
        ...     .S------7.
        ...     .|F----7|.
        ...     .||....||.
        ...     .||....||.
        ...     .|L-7F-J|.
        ...     .|..||..|.
        ...     .L--JL--J.
        ...     ..........
        ... ''').get_loop())
        F------7
        |F----7|
        ||....||
        ||....||
        |L-7F-J|
        |..||..|
        L--JL--J
        """
        (min_x, min_y), (max_x, max_y) = self.bounds
        if include_initial_empty_space:
            min_x, min_y = 0, 0
        return "\n".join(
            "".join(
                (
                    (
                        f"{self.tiles[position].value}"
                        if not box_drawing else
                        self.box_drawing_map[self.tiles[position]]
                    )
                    if not hide_pipes else
                    " "
                )
                if position in self.tiles else
                "."
                if (
                    only_empty_points is None
                    or position in only_empty_points
                ) != invert_empty_points else
                " "
                for x in range(min_x, max_x + 1)
                for position in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
        )

    def __getitem__(self, item: Point2D) -> PipeType:
        return self.tiles[item]

    def __contains__(self, item: Point2D) -> bool:
        return item in self.tiles

    def get_bound_point_count(self) -> int:
        return len(self.get_bound_points())

    def get_bound_points(self) -> Set[Point2D]:
        """
        >>> sorted(FieldExtended.from_field_text('''
        ...     .....
        ...     .S-7.
        ...     .|.|.
        ...     .L-J.
        ...     .....
        ... ''').get_loop().get_bound_points())
        [Point2D(x=2, y=2)]
        >>> sorted(FieldExtended.from_field_text('''
        ...     .......
        ...     .S---7.
        ...     .|...|.
        ...     .|...|.
        ...     .|...|.
        ...     .L---J.
        ...     .......
        ... ''').get_loop().get_bound_points())
        [Point2D(x=2, y=2), Point2D(x=2, y=3), Point2D(x=2, y=4),
            Point2D(x=3, y=2), Point2D(x=3, y=3), Point2D(x=3, y=4),
            Point2D(x=4, y=2), Point2D(x=4, y=3), Point2D(x=4, y=4)]
        >>> sorted(FieldExtended.from_field_text('''
        ...     ..........
        ...     .S------7.
        ...     .|F----7|.
        ...     .||....||.
        ...     .||....||.
        ...     .|L-7F-J|.
        ...     .|..||..|.
        ...     .L--JL--J.
        ...     ..........
        ... ''').get_loop().get_bound_points())
        [Point2D(x=2, y=6), Point2D(x=3, y=6), Point2D(x=6, y=6),
            Point2D(x=7, y=6)]
        """
        inside_points = set()
        for point in LoopCrawler.crawl_loop(self):
            if point in inside_points:
                continue
            inside_points.update(self.flood_point(point))
        return inside_points

    def is_in_bounds(self, point: Point2D) -> bool:
        return (
            (self.bounds[0].x <= point.x <= self.bounds[1].x)
            and (self.bounds[0].y <= point.y <= self.bounds[1].y)
        )

    def flood_point(self, start: Point2D) -> Set[Point2D]:
        """
        >>> loop = FieldExtended.from_field_text('''
        ...     .....
        ...     .S-7.
        ...     .|.|.
        ...     .L-J.
        ...     .....
        ... ''').get_loop()
        >>> sorted(loop.flood_point(Point2D(1, 1)))
        []
        >>> sorted(loop.flood_point(Point2D(0, 0)))
        Traceback (most recent call last):
        ...
        Exception: Start point Point2D(x=0, y=0) is not bound by the loop: it
            is outside of (1x1)-(3x3)
        >>> sorted(loop.flood_point(Point2D(2, 2)))
        [Point2D(x=2, y=2)]
        >>> sorted(FieldExtended.from_field_text('''
        ...     .....
        ...     .S--7.
        ...     .|..|.
        ...     .|..|.
        ...     .L--J.
        ...     .....
        ... ''').get_loop().flood_point(Point2D(2, 2)))
        [Point2D(x=2, y=2), Point2D(x=2, y=3), Point2D(x=3, y=2),
            Point2D(x=3, y=3)]
        """
        if start in self:
            return set()
        points = {start}
        stack = [start]

        if not self.is_in_bounds(start):
            raise Exception(
                f"Start point {start} is not bound by the loop: it is outside "
                f"of ({self.bounds[0].x}x{self.bounds[0].y})"
                f"-({self.bounds[1].x}x{self.bounds[1].y})")

        while stack:
            point = stack.pop(0)
            for neighbour in point.get_manhattan_neighbours():
                if neighbour in points:
                    continue
                if neighbour in self:
                    continue
                if not self.is_in_bounds(neighbour):
                    raise Exception(
                        f"Start point {start} is not bound by the loop: it "
                        f"reached {neighbour}, which is outside of "
                        f"({self.bounds[0].x}x{self.bounds[0].y})"
                        f"-({self.bounds[1].x}x{self.bounds[1].y})")
                points.add(neighbour)
                stack.append(neighbour)

        return points

    def get_left_most_top_most_tile(self) -> Point2D:
        """
        >>> FieldExtended.from_field_text('''
        ...     .....
        ...     .S-7.
        ...     .|.|.
        ...     .L-J.
        ...     .....
        ... ''').get_loop().get_left_most_top_most_tile()
        Point2D(x=1, y=1)
        >>> FieldExtended.from_field_text('''
        ...     ..........
        ...     .S------7.
        ...     .|F----7|.
        ...     .||....||.
        ...     .||....||.
        ...     .|L-7F-J|.
        ...     .|..||..|.
        ...     .L--JL--J.
        ...     ..........
        ... ''').get_loop().get_left_most_top_most_tile()
        Point2D(x=1, y=1)
        """
        (min_x, _), _ = self.bounds
        return min((
            position
            for position in self.tiles
            if position.x == min_x
        ), key=lambda position: position.y)


class BorderSide(Enum):
    Left = "left"
    Right = "right"


@dataclass
class BorderCrawlStep:
    left_point: Point2D
    right_point: Point2D
    next_direction: Direction
    left_points: List[Point2D]

    @classmethod
    def from_left_point_and_next_direction(
        cls, left_point: Point2D, next_direction: Direction,
    ) -> "BorderCrawlStep":
        """
        >>> BorderCrawlStep.from_left_point_and_next_direction(
        ...     Point2D(1, 1), Direction.South)
        BorderCrawlStep(left_point=Point2D(x=1, y=1),
            right_point=Point2D(x=-1, y=-1), next_direction=Direction.South,
            left_points=[Point2D(x=0, y=1), Point2D(x=1, y=0),
            Point2D(x=1, y=1)])
        """
        return cls(
            left_point,
            Point2D.ZERO_POINT.difference(left_point),
            next_direction,
            sorted({
                left_point,
                Point2D(0, left_point.y),
                Point2D(left_point.x, 0)
            } - {Point2D.ZERO_POINT}),
        )


@dataclass
class BorderCrawlInfo:
    pipe: PipeType
    step_map: Dict[Direction, BorderCrawlStep]

    @classmethod
    def from_pipe_direction_and_left_point(
        cls, pipe: PipeType, from_direction: Direction, left_point: Point2D,
    ) -> "BorderCrawlInfo":
        """
        >>> BorderCrawlInfo.from_pipe_direction_and_left_point(
        ...     PipeType.SE, Direction.West, Point2D(1, 1))
        BorderCrawlInfo(pipe=PipeType.SE, step_map={Direction.West:
            BorderCrawlStep(left_point=Point2D(x=1, y=1),
            right_point=Point2D(x=-1, y=-1), next_direction=Direction.South,
            left_points=[...]),
            Direction.North: BorderCrawlStep(left_point=Point2D(x=-1, y=-1),
            right_point=Point2D(x=1, y=1), next_direction=Direction.East,
            left_points=[...])})
        """
        same_direction, other_direction = pipe.directions
        same_opposite_direction = OppositeDirections[same_direction]
        other_opposite_direction = OppositeDirections[other_direction]
        if from_direction == other_opposite_direction:
            same_opposite_direction, other_opposite_direction = \
                other_opposite_direction, same_opposite_direction
            same_direction, other_direction = other_direction, same_direction
        elif from_direction != same_opposite_direction:
            raise Exception(
                f"Expected `from_direction` for pipe {pipe} to be one of "
                f"{same_opposite_direction} or {other_opposite_direction}, "
                f"but it was {from_direction}")
        return cls(
            pipe,
            {
                same_opposite_direction:
                BorderCrawlStep.from_left_point_and_next_direction(
                    left_point, other_direction),
                other_opposite_direction:
                BorderCrawlStep.from_left_point_and_next_direction(
                    Point2D.ZERO_POINT.difference(left_point), same_direction),
            }
        )

    def __getitem__(self, item: Direction) -> BorderCrawlStep:
        return self.step_map[item]


BorderCrawlInfoMap: Dict[PipeType, BorderCrawlInfo] = {
    PipeType.NS: BorderCrawlInfo.from_pipe_direction_and_left_point(
        PipeType.NS, Direction.South, Point2D(1, 0)),
    PipeType.WE: BorderCrawlInfo.from_pipe_direction_and_left_point(
        PipeType.WE, Direction.East, Point2D(0, -1)),
    PipeType.SE: BorderCrawlInfo.from_pipe_direction_and_left_point(
        PipeType.SE, Direction.West, Point2D(1, 1)),
    PipeType.NE: BorderCrawlInfo.from_pipe_direction_and_left_point(
        PipeType.NE, Direction.South, Point2D(1, -1)),
    PipeType.NW: BorderCrawlInfo.from_pipe_direction_and_left_point(
        PipeType.NW, Direction.East, Point2D(-1, -1)),
    PipeType.SW: BorderCrawlInfo.from_pipe_direction_and_left_point(
        PipeType.SW, Direction.North, Point2D(-1, 1)),
}


@dataclass
class LoopCrawler:
    loop: Loop

    @classmethod
    def crawl_loop(cls, loop: Loop) -> Set[Point2D]:
        return cls(loop).crawl()

    def crawl(self) -> Set[Point2D]:
        """
        >>> sorted(LoopCrawler(FieldExtended.from_field_text('''
        ...     .....
        ...     .S-7.
        ...     .|.|.
        ...     .L-J.
        ...     .....
        ... ''').get_loop()).crawl())
        [Point2D(x=2, y=2)]
        >>> sorted(LoopCrawler(FieldExtended.from_field_text('''
        ...     .......
        ...     .S---7.
        ...     .|...|.
        ...     .|...|.
        ...     .|...|.
        ...     .L---J.
        ...     .......
        ... ''').get_loop()).crawl())
        [Point2D(x=2, y=2), Point2D(x=2, y=3), Point2D(x=2, y=4),
            Point2D(x=3, y=2), Point2D(x=3, y=4),
            Point2D(x=4, y=2), Point2D(x=4, y=3), Point2D(x=4, y=4)]
        >>> sorted(LoopCrawler(FieldExtended.from_field_text('''
        ...     ..........
        ...     .S------7.
        ...     .|F----7|.
        ...     .||....||.
        ...     .||....||.
        ...     .|L-7F-J|.
        ...     .|..||..|.
        ...     .L--JL--J.
        ...     ..........
        ... ''').get_loop()).crawl())
        [Point2D(x=2, y=6), Point2D(x=3, y=6), Point2D(x=6, y=6),
            Point2D(x=7, y=6)]
        """
        start_position = position = self.loop.get_left_most_top_most_tile()
        direction = Direction.West
        inside_points = set()

        while True:
            pipe = self.loop[position]
            crawl_info = BorderCrawlInfoMap[pipe]
            next_step = crawl_info[direction]
            for left_point in next_step.left_points:
                inside_point = position.offset(left_point)
                if inside_point not in self.loop:
                    inside_points.add(inside_point)
            next_direction = next_step.next_direction
            next_position = position.offset(next_direction.offset)
            if next_position == start_position:
                break
            position, direction = next_position, next_direction

        return inside_points


Challenge.main()
challenge = Challenge()
