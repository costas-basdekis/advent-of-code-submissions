#!/usr/bin/env python3
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Dict, List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Cls, Self, PolymorphicParser


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        7067
        """
        return Cave.from_map(_input).get_energization_level()


class Direction(Enum):
    Up = "up"
    Down = "down"
    Left = "left"
    Right = "right"


@dataclass
class Cave:
    mirrors: Dict[Point2D, "Mirror"]
    width: int
    height: int

    DIRECTION_OFFSETS: ClassVar[Dict[Direction, Point2D]] = {
        Direction.Up: Point2D(0, -1),
        Direction.Down: Point2D(0, 1),
        Direction.Left: Point2D(-1, 0),
        Direction.Right: Point2D(1, 0),
    }

    DIRECTION_STR_MAP: ClassVar[Dict[Direction, str]] = {
        Direction.Up: "^",
        Direction.Down: "v",
        Direction.Left: "<",
        Direction.Right: ">",
    }

    @classmethod
    def from_map(cls, text: str) -> "Cave":
        """
        >>> print(Cave.from_map('''
        ...     .|...*....
        ...     |.-.*.....
        ...     .....|-...
        ...     ........|.
        ...     ..........
        ...     .........*
        ...     ..../.**..
        ...     .-.-/..|..
        ...     .|....-|.*
        ...     ..//.|....
        ... '''))
        .|...*....
        |.-.*.....
        .....|-...
        ........|.
        ..........
        .........*
        ..../.**..
        .-.-/..|..
        .|....-|.*
        ..//.|....
        """
        lines = text.replace("\\", "*").strip().splitlines()
        return cls(mirrors={
            Point2D(x, y): Mirror.parse(char)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
            if char != "."
        }, width=len(lines[0].strip()) if lines else 0, height=len(lines))

    def __str__(self, visitation_map: Optional[Dict[Point2D, Set[Direction]]] = None, show_energization: bool = False) -> str:
        return "\n".join(
            "".join(
                (
                    str(mirror)
                    if mirror else
                    "."
                    if not visited_directions else
                    f"{len(visited_directions)}"
                    if len(visited_directions) > 1 else
                    self.DIRECTION_STR_MAP[list(visited_directions)[0]]
                ) if not show_energization or not visitation_map else (
                    "#"
                    if position in visitation_map else
                    "."
                )
                for x in range(self.width)
                for position in [Point2D(x, y)]
                for mirror in [self.mirrors.get(position)]
                for visited_directions in [visitation_map.get(position) if visitation_map else None]
            )
            for y in range(self.height)
        )

    def show_visitation_map(self, visitation_map: Optional[Dict[Point2D, Set[Direction]]] = None) -> str:
        if visitation_map is None:
            visitation_map = self.get_visitation_map()
        return self.__str__(visitation_map=visitation_map)

    def show_energization_map(self, visitation_map: Optional[Dict[Point2D, Set[Direction]]] = None) -> str:
        if visitation_map is None:
            visitation_map = self.get_visitation_map()
        return self.__str__(visitation_map=visitation_map, show_energization=True)

    def get_energization_level(self, visitation_map: Optional[Dict[Point2D, Set[Direction]]] = None) -> int:
        """
        >>> Cave.from_map('''
        ...     .|...*....
        ...     |.-.*.....
        ...     .....|-...
        ...     ........|.
        ...     ..........
        ...     .........*
        ...     ..../.**..
        ...     .-.-/..|..
        ...     .|....-|.*
        ...     ..//.|....
        ... ''').get_energization_level()
        46
        """
        if visitation_map is None:
            visitation_map = self.get_visitation_map()
        return len(visitation_map)

    def get_visitation_map(self) -> Dict[Point2D, Set[Direction]]:
        """
        >>> print(Cave.from_map('''
        ...     .|...*....
        ...     |.-.*.....
        ...     .....|-...
        ...     ........|.
        ...     ..........
        ...     .........*
        ...     ..../.**..
        ...     .-.-/..|..
        ...     .|....-|.*
        ...     ..//.|....
        ... ''').show_visitation_map())
        >|<<<*....
        |v-.*^....
        .v...|->>>
        .v...v^.|.
        .v...v^...
        .v...v^..*
        .v../2**..
        <->-/vv|..
        .|<<<2-|.*
        .v//.|.v..
        >>> print(Cave.from_map('''
        ...     .|...*....
        ...     |.-.*.....
        ...     .....|-...
        ...     ........|.
        ...     ..........
        ...     .........*
        ...     ..../.**..
        ...     .-.-/..|..
        ...     .|....-|.*
        ...     ..//.|....
        ... ''').show_energization_map())
        ######....
        .#...#....
        .#...#####
        .#...##...
        .#...##...
        .#...##...
        .#..####..
        ########..
        .#######..
        .#...#.#..
        """
        stack: List[Tuple[Point2D, Direction]] = [(Point2D(-1, 0), Direction.Right)]
        visitation_map: Dict[Point2D, Set[Direction]] = {}
        while stack:
            item = stack.pop(0)
            position, direction = item
            mirror = self.mirrors.get(position)
            if mirror:
                next_directions = mirror.get_next_directions(direction)
            else:
                next_directions = [direction]
            for next_direction in next_directions:
                next_position = position.offset(self.DIRECTION_OFFSETS[next_direction])
                if not self.is_within_bounds(next_position):
                    continue
                next_item = (next_position, next_direction)
                if next_position in visitation_map and next_direction in visitation_map[next_position]:
                    continue
                visitation_map.setdefault(next_position, set()).add(next_direction)
                stack.append(next_item)

        return visitation_map

    def is_within_bounds(self, point: Point2D) -> bool:
        return (
            0 <= point.x < self.width
            and 0 <= point.y < self.height
        )


@dataclass
class Mirror(PolymorphicParser, ABC, root=True):
    @classmethod
    def try_parse(cls: Cls["Mirror"], text: str) -> Optional[Self["Mirror"]]:
        if text != cls.name:
            return None
        return cls()

    def __str__(self) -> str:
        return self.name

    DIRECTIONS_MAP: ClassVar[Dict[Direction, List[Direction]]]

    def get_next_directions(self, direction: Direction) -> List[Direction]:
        return self.DIRECTIONS_MAP[direction]


@Mirror.register
@dataclass
class ForwardMirror(Mirror):
    name = "/"

    DIRECTIONS_MAP: ClassVar[Dict[Direction, List[Direction]]] = {
        Direction.Up: [Direction.Right],
        Direction.Down: [Direction.Left],
        Direction.Left: [Direction.Down],
        Direction.Right: [Direction.Up],
    }


@Mirror.register
@dataclass
class BackwardsMirror(Mirror):
    name = "*"
    # name = "\"

    DIRECTIONS_MAP: ClassVar[Dict[Direction, List[Direction]]] = {
        Direction.Up: [Direction.Left],
        Direction.Down: [Direction.Right],
        Direction.Left: [Direction.Up],
        Direction.Right: [Direction.Down],
    }


@Mirror.register
@dataclass
class HorizontalSplitter(Mirror):
    name = "-"

    DIRECTIONS_MAP: ClassVar[Dict[Direction, List[Direction]]] = {
        Direction.Up: [Direction.Left, Direction.Right],
        Direction.Down: [Direction.Left, Direction.Right],
        Direction.Left: [Direction.Left],
        Direction.Right: [Direction.Right],
    }


@Mirror.register
@dataclass
class VerticalSplitter(Mirror):
    name = "|"

    DIRECTIONS_MAP: ClassVar[Dict[Direction, List[Direction]]] = {
        Direction.Up: [Direction.Up],
        Direction.Down: [Direction.Down],
        Direction.Left: [Direction.Up, Direction.Down],
        Direction.Right: [Direction.Up, Direction.Down],
    }



Challenge.main()
challenge = Challenge()
